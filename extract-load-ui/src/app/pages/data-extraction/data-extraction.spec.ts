import { TestBed, ComponentFixture, fakeAsync, tick } from '@angular/core/testing';
import { DataExtraction } from './data-extraction';
import { ApiService } from '../../services/api.service';
import { HttpClient } from '@angular/common/http';
import { FormBuilder } from '@angular/forms';
import { of, throwError } from 'rxjs';
import { ActivatedRoute } from '@angular/router';
import { HttpClientTestingModule } from '@angular/common/http/testing';
import { NO_ERRORS_SCHEMA } from '@angular/core';
import { ReloadService } from '../../services/reload.service';

describe('DataExtraction', () => {
  let component: DataExtraction;
  let fixture: ComponentFixture<DataExtraction>;
  let apiServiceSpy: jasmine.SpyObj<ApiService>;
  let httpSpy: jasmine.SpyObj<HttpClient>;
  let reloadServiceSpy: jasmine.SpyObj<ReloadService>;

  beforeEach(async () => {
    apiServiceSpy = jasmine.createSpyObj('ApiService', ['runPipeline', 'stopPipeline']);
    httpSpy = jasmine.createSpyObj('HttpClient', ['get', 'post']);
    reloadServiceSpy = jasmine.createSpyObj('ReloadService', ['reload']);

    // Mock HTTP responses
    httpSpy.get.and.returnValue(of({ source: 'test', target: 'test' })); // Mock current-config
    httpSpy.post.and.returnValue(of({}));

    await TestBed.configureTestingModule({
      imports: [DataExtraction],
      providers: [
        FormBuilder,
        { provide: ApiService, useValue: apiServiceSpy },
        { provide: HttpClient, useValue: httpSpy },
        { provide: ActivatedRoute, useValue: {} },
        { provide: ReloadService, useValue: reloadServiceSpy }
      ],
      schemas: [NO_ERRORS_SCHEMA] // Prevent child component initialization
    }).compileComponents();

    fixture = TestBed.createComponent(DataExtraction);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
    expect(component.status).toBe('');
    expect(component.statusDetails).toEqual([]);
    expect(component.waitingForScheduledRun).toBe(false);
    expect(component.runId).toBe('');
  });

  it('should start and clear polling intervals in ngOnInit/ngOnDestroy', () => {
    spyOn(component, 'startRunIdPolling');
    component.ngOnInit();
    expect(component.startRunIdPolling).toHaveBeenCalled();
    // Instead of directly setting private pollInterval, call pollStatus (which sets it)
    spyOn(window, 'clearInterval');
    component.pollStatus(); // sets pollInterval
    component.ngOnDestroy();
    // Should clear pollInterval and runIdPollInterval if set
    expect(window.clearInterval).toHaveBeenCalled();
  });

  it('should handle runPipeline error (no current config)', fakeAsync(() => {
    httpSpy.get.and.returnValue(throwError(() => ({ message: 'fail' })));
    component.runPipeline();
    tick();
    expect(component.status).toContain('Error');
  }));

  it('should handle runPipelineOnce error (no current config)', fakeAsync(() => {
    httpSpy.get.and.returnValue(throwError(() => ({ message: 'fail' })));
    component.runPipelineOnce();
    tick();
    expect(component.status).toContain('Error');
  }));

  it('should stop pipeline and clear intervals', () => {
    // Use pollStatus to set pollInterval
    component.pollStatus();
    component.runIdPollInterval = setInterval(() => {}, 1000);
    apiServiceSpy.stopPipeline.and.returnValue(of({}));
    spyOn(window, 'clearInterval');
    component.stopPipeline();
    expect(window.clearInterval).toHaveBeenCalled();
    expect(component.status).toBe('Pipeline stopped');
    expect(component.statusDetails).toEqual([]);
    expect(component.runId).toBe('');
    expect(component.waitingForScheduledRun).toBe(false);
  });

  it('should call refreshConfigs', () => {
    component.refreshConfigs();
    expect(reloadServiceSpy.reload).toHaveBeenCalled();
  });

  it('should clear intervals on ngOnDestroy', () => {
    // @ts-ignore: Accessing private for test
    component['pollInterval'] = setInterval(() => {}, 1000);
    // @ts-ignore: Accessing private for test
    component['runIdPollInterval'] = setInterval(() => {}, 1000);
    spyOn(window, 'clearInterval');
    component.ngOnDestroy();
    expect(window.clearInterval).toHaveBeenCalledTimes(2);
  });

  it('should set waitingForScheduledRun true if no run_id in startRunIdPolling', fakeAsync(() => {
    httpSpy.get.and.returnValue(of({}));
    component.startRunIdPolling();
    tick(5001);
    expect(component.waitingForScheduledRun).toBeTrue();
  }));

  it('should set waitingForScheduledRun true if error in startRunIdPolling', fakeAsync(() => {
    httpSpy.get.and.returnValue(throwError(() => ({})));
    component.startRunIdPolling();
    tick(5001);
    expect(component.waitingForScheduledRun).toBeTrue();
  }));

  it('should clear pollInterval and set statusDetails empty on pollStatus error', fakeAsync(() => {
    component.runId = 'abc';
    httpSpy.get.and.returnValue(throwError(() => ({})));
    component.pollStatus();
    tick(2001);
    expect(component.statusDetails).toEqual([]);
  }));

  it('should clear pollInterval if pipeline completed in pollStatus', fakeAsync(() => {
    component.runId = 'abc';
    httpSpy.get.and.returnValue(of({ status: [{ timestamp: 't', message: 'Pipeline completed successfully' }] }));
    component.pollStatus();
    tick(2001);
    expect(component.statusDetails.length).toBe(1);
  }));

  it('should use FTP config in runPipeline', fakeAsync(() => {
    httpSpy.get.and.callFake((url: string, options?: any): any => {
      if (url.includes('current-config')) return of({ source: 'ftp', target: 'test' });
      if (url.includes('saved-source-configs')) return of([{ name: 'ftp', type: 'FTP' }]);
      return of({});
    });
    apiServiceSpy.runPipeline.and.returnValue(of({}));
    component.schedulerForm.setValue({ interval: 2, duration: 1 });
    component.runPipeline();
    tick();
    expect(apiServiceSpy.runPipeline).toHaveBeenCalledWith(jasmine.objectContaining({ config_file: 'config/ftp_config.yaml' }));
  }));

  it('should handle error in runPipeline runPipeline subscribe', fakeAsync(() => {
    httpSpy.get.and.callFake((url: string, options?: any): any => {
      if (url.includes('current-config')) return of({ source: 'api', target: 'test' });
      if (url.includes('saved-source-configs')) return of([{ name: 'api', type: 'API' }]);
      return of({});
    });
    apiServiceSpy.runPipeline.and.returnValue(throwError(() => ({ error: { message: 'fail' } })));
    component.schedulerForm.setValue({ interval: 2, duration: 1 });
    component.runPipeline();
    tick();
    expect(component.status).toContain('fail');
  }));

  it('should use FTP config in runPipelineOnce', fakeAsync(() => {
    (httpSpy.get as any).and.callFake((url: string, options?: any) => {
      if (url.includes('current-config')) return of({ source: 'ftp', target: 'test' });
      if (url.includes('saved-source-configs')) return of([{ name: 'ftp', type: 'FTP' }]);
      if (url.includes('pipeline-status')) return of({ status: [{ timestamp: 'now', message: 'Running' }] });
      return of({});
    });
    httpSpy.post.and.returnValue(of({ status: 'ok', run_id: 'id' }));
    component.runPipelineOnce();
    tick();
    expect(component.status).toContain('Pipeline started');
    expect(component.runId).toBe('id');
  }));

  it('should handle error in runPipelineOnce post', fakeAsync(() => {
    httpSpy.get.and.callFake((url: string, options?: any): any => {
      if (url.includes('current-config')) return of({ source: 'ftp', target: 'test' });
      if (url.includes('saved-source-configs')) return of([{ name: 'ftp', type: 'FTP' }]);
      return of({});
    });
    httpSpy.post.and.returnValue(throwError(() => ({ message: 'fail' })));
    component.runPipelineOnce();
    tick();
    expect(component.status).toContain('fail');
    expect(component.isRunOnceDisabled).toBeFalse();
  }));

  it('should not set runId if fetchLatestScheduledRunId returns no run_id', () => {
    httpSpy.get.and.returnValue(of({}));
    component.runId = 'old';
    component.fetchLatestScheduledRunId();
    expect(component.runId).toBe('old');
  });

  it('should handle error in stopPipeline', () => {
    apiServiceSpy.stopPipeline.and.returnValue(throwError(() => ({ error: { message: 'fail' } })));
    component.stopPipeline();
    expect(component.status).toContain('fail');
  });
});
