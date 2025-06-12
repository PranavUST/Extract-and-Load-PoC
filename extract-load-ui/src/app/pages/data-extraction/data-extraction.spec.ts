import { TestBed, ComponentFixture, fakeAsync, tick } from '@angular/core/testing';
import { DataExtraction } from './data-extraction';
import { ApiService } from '../../services/api.service';
import { HttpClient } from '@angular/common/http';
import { FormBuilder } from '@angular/forms';
import { of, throwError } from 'rxjs';
import { ActivatedRoute } from '@angular/router';
import { HttpClientTestingModule } from '@angular/common/http/testing';
import { NO_ERRORS_SCHEMA } from '@angular/core';

describe('DataExtraction', () => {
  let component: DataExtraction;
  let fixture: ComponentFixture<DataExtraction>;
  let apiServiceSpy: jasmine.SpyObj<ApiService>;
  let httpSpy: jasmine.SpyObj<HttpClient>;

  beforeEach(async () => {
    apiServiceSpy = jasmine.createSpyObj('ApiService', ['runPipeline', 'stopPipeline']);
    httpSpy = jasmine.createSpyObj('HttpClient', ['get', 'post']);

    // Mock HTTP responses
    httpSpy.get.and.returnValue(of({ source: 'test', target: 'test' })); // Mock current-config
    httpSpy.post.and.returnValue(of({}));

    await TestBed.configureTestingModule({
      imports: [DataExtraction],
      providers: [
        FormBuilder,
        { provide: ApiService, useValue: apiServiceSpy },
        { provide: HttpClient, useValue: httpSpy },
        { provide: ActivatedRoute, useValue: {} }
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
});
