import { inject } from '@angular/core';
import { CanActivateFn, Router } from '@angular/router';
import { map, catchError, of } from 'rxjs';
import { AuthService } from './auth.service';

export const adminGuard: CanActivateFn = () => {
  const auth = inject(AuthService);
  const router = inject(Router);
  if (auth.currentUser()) return auth.isAdmin() ? true : router.createUrlTree(['/dashboard']);
  return auth.loadCurrentUser().pipe(
    map(user => user.role === 'admin' ? true : router.createUrlTree(['/dashboard'])),
    catchError(() => of(router.createUrlTree(['/login']))),
  );
};
