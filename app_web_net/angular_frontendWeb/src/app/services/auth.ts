import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, tap } from 'rxjs';
import { environment } from '../../environments/environment';
import { SesionService } from './sesion';

export interface LoginResponse {
  id: number;
  nombre: string;
  correo: string;
  rol: string;
  organizacionId: number;
  estado_Activo: boolean;
  mensaje: string;
}

@Injectable({ providedIn: 'root' })
export class AuthService {
  private apiUrl = `${environment.apiUrl}/api/usuarios`;
  private sesionService = inject(SesionService);

  constructor(private http: HttpClient) {}

  login(correo: string, contrasena: string): Observable<LoginResponse> {
    return this.http
      .post<LoginResponse>(`${this.apiUrl}/login`, { correo, contrasena })
      .pipe(tap((respuesta) => this.sesionService.guardarSesion(respuesta)));
  }

  logout(): void {
    this.sesionService.cerrarSesion();
  }
}
