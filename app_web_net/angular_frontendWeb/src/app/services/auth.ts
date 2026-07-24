import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

export interface LoginResponse {
  id: number;
  nombre: string;
  correo: string;
  rol: string;
  organizacionId: number;
  estado_Activo: boolean;
  mensaje: string;
}

@Injectable({
  providedIn: 'root'
})
export class AuthService {

  private apiUrl = 'https://lmsidgs902.runasp.net/api/usuarios';

  constructor(private http: HttpClient) {}

  login(correo: string, contrasena: string): Observable<LoginResponse> {

    return this.http.post<LoginResponse>(
      `${this.apiUrl}/login`,
      {
        correo,
        contrasena
      }
    );

  }

}