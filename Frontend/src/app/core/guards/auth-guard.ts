import { CanActivateFn, Router } from '@angular/router';
import { inject, PLATFORM_ID } from '@angular/core';
import { isPlatformBrowser } from '@angular/common';

import { TokenService } from '../services/token';

export const authGuard: CanActivateFn = () => {

  const tokenService = inject(TokenService);
  const router = inject(Router);

  const platformId = inject(PLATFORM_ID);

  if (!isPlatformBrowser(platformId)) {
    return router.createUrlTree(['/auth/login']);
  }

  if (tokenService.isLoggedIn()) {
    return true;
  }

  return router.createUrlTree([
    '/auth/login'
  ]);

};