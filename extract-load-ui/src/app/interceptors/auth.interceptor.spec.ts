import { AuthInterceptor } from './auth.interceptor';

describe('AuthInterceptor', () => {
  it('should clone the request with credentials and call next', () => {
    const req = { clone: jasmine.createSpy('clone').and.callFake((opts: any) => ({ ...req, ...opts })) } as any;
    const next = jasmine.createSpy('next');
    AuthInterceptor(req, next);
    expect(req.clone).toHaveBeenCalledWith({ withCredentials: true });
    expect(next).toHaveBeenCalledWith(jasmine.objectContaining({ withCredentials: true }));
  });
});
