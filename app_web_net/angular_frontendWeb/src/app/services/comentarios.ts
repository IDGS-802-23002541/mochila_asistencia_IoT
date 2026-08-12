import { HttpClient } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';
import { Comentario, CrearComentarioDto, ActualizarComentarioDto } from '../interfaces/comentario';
import { environment } from '../../environments/environment';

@Injectable({
  providedIn: 'root'
})
export class ComentariosService {
  private http = inject(HttpClient);
  private readonly baseUrl = `${environment.apiUrl}/api/comentarios`;

  obtenerTodos(estado?: string): Observable<Comentario[]> {
    const url = estado ? `${this.baseUrl}?estado=${estado}` : this.baseUrl;
    return this.http.get<Comentario[]>(url);
  }

  obtenerPorId(id: number): Observable<Comentario> {
    return this.http.get<Comentario>(`${this.baseUrl}/${id}`);
  }

  crear(dto: CrearComentarioDto): Observable<any> {
    return this.http.post(this.baseUrl, dto);
  }

  actualizar(id: number, dto: ActualizarComentarioDto): Observable<any> {
    return this.http.put(`${this.baseUrl}/${id}`, dto);
  }

  eliminar(id: number): Observable<any> {
    return this.http.delete(`${this.baseUrl}/${id}`);
  }
}
