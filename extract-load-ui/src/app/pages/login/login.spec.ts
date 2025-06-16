import { ComponentFixture, TestBed } from '@angular/core/testing';
import { LoginComponent } from './login';
import { HttpClientTestingModule } from '@angular/common/http/testing';
import { ActivatedRoute } from '@angular/router';

describe('LoginComponent', () => {
  let component: LoginComponent;
  let fixture: ComponentFixture<LoginComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [HttpClientTestingModule, LoginComponent],
      providers: [{ provide: ActivatedRoute, useValue: {} }]
    }).compileComponents();
    fixture = TestBed.createComponent(LoginComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should not submit if username or password is empty', () => {
    component.username = '';
    component.password = '';
    component.onSubmit();
    expect(component.loginError).toBe(false);
  });

  it('should set loginError and errorMessage on failed login', () => {
    const authService = (component as any).authService;
    spyOn(authService, 'login').and.returnValue({ subscribe: (handlers: any) => handlers.next({ success: false }) });
    component.username = 'user';
    component.password = 'wrong';
    component.onSubmit();
    expect(component.loginError).toBe(true);
    expect(component.errorMessage).toBe('Invalid Username or Password');
  });

  it('should navigate on successful login', () => {
    const authService = (component as any).authService;
    const router = (component as any).router;
    spyOn(authService, 'login').and.returnValue({ subscribe: (handlers: any) => handlers.next({ success: true }) });
    spyOn(router, 'navigate');
    component.username = 'user';
    component.password = 'pass';
    component.onSubmit();
    expect(router.navigate).toHaveBeenCalledWith(['/landing']);
  });

  it('should toggle password visibility', () => {
    const initial = component.hidePassword;
    component.togglePasswordVisibility();
    expect(component.hidePassword).toBe(!initial);
  });
});
