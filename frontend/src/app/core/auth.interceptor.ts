import { HttpInterceptorFn } from '@angular/common/http';

export const authInterceptor: HttpInterceptorFn = (request, next) => {
  const token = localStorage.getItem('access_token');
  if (!token || request.url.endsWith('/auth/login') || request.url.endsWith('/auth/register')) {
    return next(request);
  }
  const authorization = ['Bearer', token].join(' ');
  return next(request.clone({ setHeaders: { Authorization: authorization } }));
};
