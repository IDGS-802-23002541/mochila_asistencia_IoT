import { inject } from '@angular/core';
import { CanActivateFn, Router } from '@angular/router';
import { SesionService } from '../services/sesion';

export const authGuard: CanActivateFn = () => {
  const sesionService = inject(SesionService);
  const router = inject(Router);

  if (sesionService.estaAutenticado()) return true;

  router.navigate(['/login']);
  return false;
};
