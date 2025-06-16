import { ComponentFixture, TestBed } from '@angular/core/testing';
import { HttpClientTestingModule } from '@angular/common/http/testing';
import { ActivatedRoute } from '@angular/router';
import { FormBuilder } from '@angular/forms';
import { ProfileComponent } from './profile';
import { ApiService } from '../../core/services/api';
import { throwError } from 'rxjs';

describe('ProfileComponent', () => {
  let component: ProfileComponent;
  let fixture: ComponentFixture<ProfileComponent>;
  let apiSpy: jasmine.SpyObj<ApiService>;

  beforeEach(async () => {
    apiSpy = jasmine.createSpyObj('ApiService', [
      'getProfile', 'updateUser', 'changePassword'
    ]);
    await TestBed.configureTestingModule({
      imports: [HttpClientTestingModule, ProfileComponent],
      providers: [
        { provide: ActivatedRoute, useValue: {} },
        { provide: ApiService, useValue: apiSpy },
        FormBuilder
      ]
    }).compileComponents();
    fixture = TestBed.createComponent(ProfileComponent);
    component = fixture.componentInstance;
    // Don't call detectChanges to avoid ngOnInit HTTP
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should start edit and patch form', () => {
    component.user = { name: 'A', email: 'a@b.com', username: 'a' };
    component.startEdit();
    expect(component.editing).toBeTrue();
    expect(component.profileForm.value.name).toBe('A');
  });

  it('should cancel edit and patch form', () => {
    component.user = { name: 'A', email: 'a@b.com', username: 'a' };
    component.cancelEdit();
    expect(component.editing).toBeFalse();
    expect(component.profileForm.value.name).toBe('A');
  });

  it('should not save profile if invalid', () => {
    component.user = { id: 1 };
    component.profileForm.setErrors({ invalid: true });
    component.saveProfile();
    expect(component.saving).toBeFalse();
  });

  it('should toggle password form', () => {
    component.showPasswordForm = false;
    component.togglePasswordForm();
    expect(component.showPasswordForm).toBeTrue();
  });

  it('should not save profile if user or user.id is missing', () => {
    component.user = undefined as any;
    component.saveProfile();
    expect(component.saving).toBeFalse();
    component.user = { id: undefined };
    component.saveProfile();
    expect(component.saving).toBeFalse();
  });

  it('should mark form as touched and not save if form invalid', () => {
    component.user = { id: 1 };
    spyOn(component.profileForm, 'markAllAsTouched');
    component.profileForm.setErrors({ invalid: true });
    component.saveProfile();
    expect(component.profileForm.markAllAsTouched).toHaveBeenCalled();
  });

  it('should return mismatch in passwordsMatchValidator', () => {
    const form = new FormBuilder().group({ newPassword: 'a', confirmPassword: 'b' });
    expect(component.passwordsMatchValidator(form)).toEqual({ mismatch: true });
  });

  it('should not change password if form invalid', () => {
    component.passwordForm.setErrors({ invalid: true });
    spyOn(component.passwordForm, 'markAllAsTouched');
    component.changePassword();
    expect(component.passwordForm.markAllAsTouched).toHaveBeenCalled();
  });
});
