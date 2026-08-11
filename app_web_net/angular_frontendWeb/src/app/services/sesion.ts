import { Injectable, signal, computed } from '@angular/core';
import { LoginResponse } from './auth';

const SESSION_KEY = 'usuario';

@Injectable({ providedIn: 'root' })
export class SesionService {
  private readonly _sesion = signal<LoginResponse | null>(this.leerDeStorage());

  readonly sesion = this._sesion.asReadonly();
  readonly estaAutenticado = computed(() => this._sesion() !== null);

  readonly esOrganizacion = computed(() => this._sesion()?.rol === 'admin' || this._sesion()?.rol === 'organizacion');
  readonly organizacionId = computed(() => this._sesion()?.organizacionId ?? null);
  readonly usuarioId = computed(() => this._sesion()?.id ?? null);

  guardarSesion(respuesta: LoginResponse): void {
    localStorage.setItem(SESSION_KEY, JSON.stringify(respuesta));
    this._sesion.set(respuesta);
  }

  obtenerUsuario(): any | null {
    const usuario = localStorage.getItem('usuario');

    return usuario
      ? JSON.parse(usuario)
      : null;
  }

  obtenerRol(): string | null {
    return this.obtenerUsuario()?.rol ?? null;
  }

  cerrarSesion(): void {
    localStorage.removeItem(SESSION_KEY);
    this._sesion.set(null);
  }

  private leerDeStorage(): LoginResponse | null {
    const raw = localStorage.getItem(SESSION_KEY);
    if (!raw) return null;
    try {
      return JSON.parse(raw) as LoginResponse;
    } catch {
      localStorage.removeItem(SESSION_KEY);
      return null;
    }
  }
}
