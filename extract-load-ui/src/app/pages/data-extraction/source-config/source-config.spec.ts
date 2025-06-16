import { ComponentFixture, TestBed } from '@angular/core/testing';
import { ReactiveFormsModule } from '@angular/forms';
import { HttpClientTestingModule } from '@angular/common/http/testing';
import { SourceConfig } from './source-config';

describe('SourceConfig', () => {
  let component: SourceConfig;
  let fixture: ComponentFixture<SourceConfig>;

  beforeAll(() => {
    spyOn(window, 'alert');
  });

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ReactiveFormsModule, HttpClientTestingModule, SourceConfig]
    }).compileComponents();
    fixture = TestBed.createComponent(SourceConfig);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should set validators for API type', () => {
    component.sourceForm.get('type')?.setValue('API');
    component.sourceForm.get('endpoint')?.setValue('');
    component.sourceForm.get('ftpHost')?.setValue('host');
    component.sourceForm.get('ftpUsername')?.setValue('user');
    component.sourceForm.get('ftpPassword')?.setValue('pass');
    expect(component.sourceForm.get('endpoint')?.validator).toBeTruthy();
    expect(component.sourceForm.get('ftpHost')?.validator).toBeNull();
    expect(component.sourceForm.get('ftpUsername')?.validator).toBeNull();
    expect(component.sourceForm.get('ftpPassword')?.validator).toBeNull();
  });

  it('should set validators for FTP type', () => {
    component.sourceForm.get('type')?.setValue('FTP');
    component.sourceForm.get('ftpHost')?.setValue('');
    component.sourceForm.get('endpoint')?.setValue('endpoint');
    expect(component.sourceForm.get('ftpHost')?.validator).toBeTruthy();
    expect(component.sourceForm.get('endpoint')?.validator).toBeNull();
  });

  it('should emit configSaved when saveConfig is called', () => {
    spyOn(component.configSaved, 'emit');
    // Make form valid
    component.sourceForm.patchValue({
      name: 'Test',
      type: 'API',
      endpoint: 'http://test',
      authToken: 'token',
      ftpHost: '',
      ftpUsername: '',
      ftpPassword: '',
      retries: 1
    });
    // Mock api.saveSourceConfig to immediately call next
    const api = (component as any).api;
    spyOn(api, 'saveSourceConfig').and.returnValue({ subscribe: (handlers: any) => handlers.next({}) });
    component.saveConfig();
    expect(component.configSaved.emit).toHaveBeenCalled();
  });
});
