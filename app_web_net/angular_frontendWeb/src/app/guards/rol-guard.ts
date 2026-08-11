import { inject } from '@angular/core';
import { CanActivateFn, Router } from '@angular/router';
import { SesionService } from '../services/sesion';

export function rolGuard(rolesPermitidos: string[]): CanActivateFn {

  return () => {

    const sesion = inject(SesionService);
    const router = inject(Router);

    // No está autenticado
    if (!sesion.estaAutenticado()) {
      return router.createUrlTree(['/login']);
    }

    const rol = sesion.obtenerRol();

    // Tiene el rol permitido
    if (rol && rolesPermitidos.includes(rol)) {
      return true;
    }

    // Está autenticado pero no tiene permiso
    if (rol === 'admin') {
      return router.createUrlTree(['/inicio']);
    }

    if (rol === 'usuario') {
      return router.createUrlTree(['/inicio']);
    }

    return router.createUrlTree(['/login']);
  };
}
