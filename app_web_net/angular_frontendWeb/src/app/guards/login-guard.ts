import { inject } from '@angular/core';
import { CanActivateFn, Router } from '@angular/router';
import { SesionService } from '../services/sesion';

export const loginGuard: CanActivateFn = () => {
  const sesion = inject(SesionService);
  const router = inject(Router);

  if (sesion.estaAutenticado()) {
    return router.createUrlTree(['/inicio']);
  }

  return true;
};
