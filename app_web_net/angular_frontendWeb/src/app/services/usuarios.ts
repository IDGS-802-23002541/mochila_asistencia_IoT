import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';
import { Usuario } from '../interfaces/usuario';

@Injectable({ providedIn: 'root' })
export class UsuariosService {
  private apiUrl = `${environment.apiUrl}/api/usuarios`;

  constructor(private http: HttpClient) {}

  getById(id: number): Observable<Usuario> {
    return this.http.get<Usuario>(`${this.apiUrl}/${id}`);
  }

  update(id: number, usuario: Usuario): Observable<Usuario> {
    return this.http.put<Usuario>(`${this.apiUrl}/${id}`, usuario);
  }
}
