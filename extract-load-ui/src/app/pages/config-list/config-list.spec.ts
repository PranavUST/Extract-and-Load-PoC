import { ComponentFixture, TestBed } from '@angular/core/testing';
import { HttpClientTestingModule } from '@angular/common/http/testing';
import { MatDialog } from '@angular/material/dialog';
import { NO_ERRORS_SCHEMA } from '@angular/core';
import { ConfigListComponent } from './config-list';
import { HttpClient } from '@angular/common/http';
import { of, throwError } from 'rxjs';
import { MatDialogRef } from '@angular/material/dialog';

describe('ConfigListComponent', () => {
  let component: ConfigListComponent;
  let fixture: ComponentFixture<ConfigListComponent>;
  let dialogSpy: any;

  function createDialogRefMock(result: any) {
    return {
      close: jasmine.createSpy('close'),
      afterClosed: () => of(result),
      afterOpened: () => of(undefined),
      beforeClosed: () => of(undefined),
      backdropClick: () => of(undefined),
      keydownEvents: () => of(undefined),
      updatePosition: jasmine.createSpy('updatePosition'),
      updateSize: jasmine.createSpy('updateSize'),
      addPanelClass: jasmine.createSpy('addPanelClass'),
      removePanelClass: jasmine.createSpy('removePanelClass'),
      componentInstance: {},
      _afterAllClosed: of(undefined),
    };
  }

  beforeEach(async () => {
    dialogSpy = jasmine.createSpyObj('MatDialog', ['open']);
    dialogSpy._openedDialogs = [];
    dialogSpy.open.and.callFake((...args: any[]) => {
      // If a test sets a specific return value, use it
      if (dialogSpy.open.and.returnValue) {
        return dialogSpy.open.and.returnValue();
      }
      // Otherwise, push a default dialogRef
      const ref = createDialogRefMock(null);
      dialogSpy._openedDialogs.push(ref);
      return ref;
    });

    await TestBed.configureTestingModule({
      imports: [HttpClientTestingModule, ConfigListComponent],
      providers: [
        { provide: MatDialog, useValue: dialogSpy }
      ],
      schemas: [NO_ERRORS_SCHEMA]
    }).compileComponents();

    fixture = TestBed.createComponent(ConfigListComponent);
    component = fixture.componentInstance;
    // Do NOT call fixture.detectChanges() to avoid ngOnInit HTTP calls and subscribe errors
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should call loadSourceConfigs, loadTargetConfigs, and loadCurrentConfig on ngOnInit', () => {
    const loadSourceConfigsSpy = spyOn(component as any, 'loadSourceConfigs');
    const loadTargetConfigsSpy = spyOn(component as any, 'loadTargetConfigs');
    const loadCurrentConfigSpy = spyOn(component as any, 'loadCurrentConfig');
    component.ngOnInit();
    expect(loadSourceConfigsSpy).toHaveBeenCalled();
    expect(loadTargetConfigsSpy).toHaveBeenCalled();
    expect(loadCurrentConfigSpy).toHaveBeenCalled();
  });

  describe('deleteSourceConfig', () => {
    it('should call delete and reload configs on confirm', () => {
      spyOn(window, 'confirm').and.returnValue(true);
      const http = TestBed.inject(HttpClient);
      spyOn(http, 'delete').and.returnValue(of({}));
      const loadSourceConfigsSpy = spyOn(component as any, 'loadSourceConfigs');
      const loadCurrentConfigSpy = spyOn(component as any, 'loadCurrentConfig');
      component.deleteSourceConfig({ name: 'test', type: 'api' });
      expect(loadSourceConfigsSpy).toHaveBeenCalled();
      expect(loadCurrentConfigSpy).toHaveBeenCalled();
    });
    it('should not call delete if confirm is false', () => {
      spyOn(window, 'confirm').and.returnValue(false);
      const http = TestBed.inject(HttpClient);
      const deleteSpy = spyOn(http, 'delete');
      component.deleteSourceConfig({ name: 'test', type: 'api' });
      expect(deleteSpy).not.toHaveBeenCalled();
    });
    it('should alert on error', () => {
      spyOn(window, 'confirm').and.returnValue(true);
      const http = TestBed.inject(HttpClient);
      spyOn(http, 'delete').and.returnValue(throwError(() => ({ message: 'fail' })));
      const alertSpy = spyOn(window, 'alert');
      component.deleteSourceConfig({ name: 'test', type: 'api' });
      expect(alertSpy).toHaveBeenCalled();
    });
  });

  describe('deleteTargetConfig', () => {
    it('should call delete and reload configs on confirm', () => {
      spyOn(window, 'confirm').and.returnValue(true);
      const http = TestBed.inject(HttpClient);
      spyOn(http, 'delete').and.returnValue(of({}));
      const loadTargetConfigsSpy = spyOn(component as any, 'loadTargetConfigs');
      const loadCurrentConfigSpy = spyOn(component as any, 'loadCurrentConfig');
      component.deleteTargetConfig({ name: 'test' });
      expect(loadTargetConfigsSpy).toHaveBeenCalled();
      expect(loadCurrentConfigSpy).toHaveBeenCalled();
    });
    it('should not call delete if confirm is false', () => {
      spyOn(window, 'confirm').and.returnValue(false);
      const http = TestBed.inject(HttpClient);
      const deleteSpy = spyOn(http, 'delete');
      component.deleteTargetConfig({ name: 'test' });
      expect(deleteSpy).not.toHaveBeenCalled();
    });
    it('should alert on error', () => {
      spyOn(window, 'confirm').and.returnValue(true);
      const http = TestBed.inject(HttpClient);
      spyOn(http, 'delete').and.returnValue(throwError(() => ({ message: 'fail' })));
      const alertSpy = spyOn(window, 'alert');
      component.deleteTargetConfig({ name: 'test' });
      expect(alertSpy).toHaveBeenCalled();
    });
  });

  describe('setCurrentSource', () => {
    it('should set currentSource on success', () => {
      const http = TestBed.inject(HttpClient);
      spyOn(http, 'post').and.returnValue(of({}));
      component.currentTarget = 'target';
      component.setCurrentSource('source');
      expect(component.currentSource).toBe('source');
    });
  });

  describe('setCurrentTarget', () => {
    it('should set currentTarget on success', () => {
      const http = TestBed.inject(HttpClient);
      spyOn(http, 'post').and.returnValue(of({}));
      component.currentSource = 'source';
      component.setCurrentTarget('target');
      expect(component.currentTarget).toBe('target');
    });
  });

  describe('debugConfigs', () => {
    it('should call http.get and log', () => {
      const http = TestBed.inject(HttpClient);
      spyOn(http, 'get').and.returnValue(of({}));
      const logSpy = spyOn(console, 'log');
      component.debugConfigs();
      expect(logSpy).toHaveBeenCalled();
    });
    it('should log error on http error', () => {
      const http = TestBed.inject(HttpClient);
      spyOn(http, 'get').and.returnValue(throwError(() => 'fail'));
      const errorSpy = spyOn(console, 'error');
      component.debugConfigs();
      expect(errorSpy).toHaveBeenCalled();
    });
  });
});
