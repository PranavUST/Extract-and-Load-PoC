import { ComponentFixture, TestBed } from '@angular/core/testing';
import { FormBuilder, ReactiveFormsModule } from '@angular/forms';
import { HttpClientTestingModule } from '@angular/common/http/testing';
import { ActivatedRoute } from '@angular/router';
import { RouterTestingModule } from '@angular/router/testing';
import { of, throwError } from 'rxjs';

import { Register } from './register';
import { AuthService } from '../../services/auth.service';
import { Router } from '@angular/router';

export {}; // Ensure this file is treated as a module

describe('Register', () => {
  let component: Register;
  let fixture: ComponentFixture<Register>;
  let authSpy: jasmine.SpyObj<AuthService>;

  beforeEach(async () => {
    authSpy = jasmine.createSpyObj('AuthService', ['register']);
    await TestBed.configureTestingModule({
      imports: [ReactiveFormsModule, HttpClientTestingModule, Register, RouterTestingModule],
      providers: [
        { provide: ActivatedRoute, useValue: {} },
        { provide: AuthService, useValue: authSpy }
      ]
    }).compileComponents();
    fixture = TestBed.createComponent(Register);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should not submit if form invalid', () => {
    component.registerForm.setErrors({ invalid: true });
    component.onSubmit();
    expect(authSpy.register).not.toHaveBeenCalled();
  });

  it('should submit and navigate on successful registration', () => {
    component.registerForm.setValue({
      name: 'Test', email: 'test@test.com', username: 'testuser', password: 'abcdef', role: 'User'
    });
    const router = TestBed.inject(Router);
    spyOn(router, 'navigate');
    authSpy.register.and.returnValue(of({ success: true }));
    component.onSubmit();
    expect(router.navigate).toHaveBeenCalledWith(['/login']);
  });

  it('should set errorMessage on registration error response', () => {
    component.registerForm.setValue({
      name: 'Test', email: 'test@test.com', username: 'testuser', password: 'abcdef', role: 'User'
    });
    authSpy.register.and.returnValue(of({ success: false, error: 'fail' }));
    component.onSubmit();
    expect(component.errorMessage).toBe('fail');
  });

  it('should set errorMessage on registration HTTP error', () => {
    component.registerForm.setValue({
      name: 'Test', email: 'test@test.com', username: 'testuser', password: 'abcdef', role: 'User'
    });
    authSpy.register.and.returnValue(throwError(() => ({ error: { error: 'fail' } })));
    component.onSubmit();
    expect(component.errorMessage).toBe('fail');
  });
});
