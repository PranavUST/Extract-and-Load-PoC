import { ComponentFixture, TestBed } from '@angular/core/testing';
import { ReactiveFormsModule } from '@angular/forms';
import { HttpClientTestingModule } from '@angular/common/http/testing';
import { TargetConfig } from './target-config';
import { of, throwError } from 'rxjs';

describe('TargetConfig', () => {
  let component: TargetConfig;
  let fixture: ComponentFixture<TargetConfig>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ReactiveFormsModule, HttpClientTestingModule, TargetConfig]
    }).compileComponents();
    fixture = TestBed.createComponent(TargetConfig);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  describe('saveConfig', () => {
    it('should call api and emit on success', () => {
      component.targetForm.setValue({ name: 't', type: 'Database', tableName: 'tbl' });
      const api = (component as any).api;
      spyOn(api, 'saveTargetConfig').and.returnValue(of({}));
      const emitSpy = spyOn(component.configSaved, 'emit');
      spyOn(window, 'alert');
      component.saveConfig();
      expect(api.saveTargetConfig).toHaveBeenCalled();
      expect(window.alert).toHaveBeenCalledWith('Target config saved!');
      expect(emitSpy).toHaveBeenCalled();
    });
    it('should alert on error', () => {
      component.targetForm.setValue({ name: 't', type: 'Database', tableName: 'tbl' });
      const api = (component as any).api;
      spyOn(api, 'saveTargetConfig').and.returnValue(throwError(() => ({ message: 'fail' })));
      spyOn(window, 'alert');
      component.saveConfig();
      expect(window.alert).toHaveBeenCalledWith('Save failed: fail');
    });
    it('should not call api if form invalid', () => {
      component.targetForm.setErrors({ invalid: true });
      const api = (component as any).api;
      const spy = spyOn(api, 'saveTargetConfig');
      component.saveConfig();
      expect(spy).not.toHaveBeenCalled();
    });
  });
});
