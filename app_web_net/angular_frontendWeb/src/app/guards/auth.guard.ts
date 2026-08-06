import { inject } from '@angular/core';
import { CanActivateFn, Router } from '@angular/router';
import { SesionService } from '../services/sesion';

export const authGuard: CanActivateFn = () => {
  const sesionService = inject(SesionService);
  const router = inject(Router);

  return sesionService.estaAutenticado()
    ? true
    : router.createUrlTree(['/login']);
};
