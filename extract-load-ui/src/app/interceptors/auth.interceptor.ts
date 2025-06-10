// src/app/interceptors/auth.interceptor.ts
import { HttpInterceptorFn } from '@angular/common/http';

export const AuthInterceptor: HttpInterceptorFn = (req, next) => {
  // Clone request with credentials
  const authReq = req.clone({
    withCredentials: true
  });
  
  // Pass to next handler (no .handle() method)
  return next(authReq);
};
