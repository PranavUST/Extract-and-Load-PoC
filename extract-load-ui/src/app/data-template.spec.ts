import { ComponentFixture, TestBed } from '@angular/core/testing';
import { HttpClientTestingModule } from '@angular/common/http/testing';
import { of, throwError } from 'rxjs';

import { DataTemplateComponent } from './data-template';

describe('DataTemplate', () => {
  let component: DataTemplateComponent;
  let fixture: ComponentFixture<DataTemplateComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [HttpClientTestingModule, DataTemplateComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(DataTemplateComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  describe('runPipeline', () => {
    it('should set error if configFile is empty', () => {
      component.configFile = '';
      component.runPipeline();
      expect(component.status).toContain('Error:');
    });
    it('should set status and log on success', () => {
      component.configFile = 'file';
      const pipelineService = (component as any).pipelineService;
      spyOn(pipelineService, 'runPipeline').and.returnValue(of({}));
      spyOn(console, 'log');
      component.runPipeline();
      expect(component.status).toBe('Pipeline started!');
      expect(console.log).toHaveBeenCalled();
    });
    it('should set error status and log on error', () => {
      component.configFile = 'file';
      const pipelineService = (component as any).pipelineService;
      spyOn(pipelineService, 'runPipeline').and.returnValue(throwError(() => ({ error: { message: 'fail' } })));
      spyOn(console, 'error');
      component.runPipeline();
      expect(component.status).toContain('Error:');
      expect(console.error).toHaveBeenCalled();
    });
  });

  describe('checkStatus', () => {
    it('should set status on success', () => {
      const pipelineService = (component as any).pipelineService;
      spyOn(pipelineService, 'getStatus').and.returnValue(of({ status: 'success', message: 'msg' }));
      component.checkStatus();
      expect(component.status).toContain('Status: success');
    });
    it('should set error status and log on error', () => {
      const pipelineService = (component as any).pipelineService;
      spyOn(pipelineService, 'getStatus').and.returnValue(throwError(() => ({ error: { message: 'fail' } })));
      spyOn(console, 'error');
      component.checkStatus();
      expect(component.status).toContain('Error:');
      expect(console.error).toHaveBeenCalled();
    });
  });
});
