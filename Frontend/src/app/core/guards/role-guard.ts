import { CanActivateFn, Router } from '@angular/router';
import { inject } from '@angular/core';
import { TokenService } from '../services/token';

export const roleGuard: CanActivateFn = (route) => {
  const tokenService = inject(TokenService);
  const router = inject(Router);

  if (!tokenService.isLoggedIn()) {
    return router.createUrlTree(['/auth/login']);
  }

  const allowedRoles: string[] = route.data?.['roles'] ?? [];
  if (allowedRoles.length === 0) {
    return true;
  }

  const session = tokenService.getUserData();
  const rawRoles: string[] = session?.roles ?? [];

  // Normalizar nombres de roles para hacer comparaciones insensibles a formato
  const userRoles = rawRoles.map((r) =>
    r
      .toLowerCase()
      .trim()
      .replace(/[áäâ]/g, 'a')
      .replace(/[óöô]/g, 'o')
      .replace(/[úüû]/g, 'u')
      .replace(/[éëê]/g, 'e')
      .replace(/[íïî]/g, 'i')
  );

  const hasPermission = allowedRoles.some((allowed) => {
    const normAllowed = allowed
      .toLowerCase()
      .trim()
      .replace(/[áäâ]/g, 'a')
      .replace(/[óöô]/g, 'o')
      .replace(/[úüû]/g, 'u')
      .replace(/[éëê]/g, 'e')
      .replace(/[íïî]/g, 'i');

    return userRoles.some((userRole) => userRole.includes(normAllowed) || normAllowed.includes(userRole));
  });

  if (hasPermission) {
    return true;
  }

  console.warn(`Acceso denegado a la ruta ${route.url}. Roles requeridos:`, allowedRoles);
  return router.createUrlTree(['/app/dashboard']);
};
