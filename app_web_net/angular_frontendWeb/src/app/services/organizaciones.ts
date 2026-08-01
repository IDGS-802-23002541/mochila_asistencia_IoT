import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';
import { Organizacion } from '../interfaces/organizacion';

@Injectable({
  providedIn: 'root',
})

export class OrganizacionesService {
  private readonly baseUrl = `${environment.apiUrl}/api/organizaciones`;

  constructor(private http: HttpClient) {}

  // metodo para obtener todas las organizaciones
  getAll(): Observable<Organizacion[]> {
    return this.http.get<Organizacion[]>(this.baseUrl);
  }

  // metodo para obtener una organizacion por su id
  getById(id: number): Observable<Organizacion> {
    return this.http.get<Organizacion>(`${this.baseUrl}/${id}`);
  }

  // metodo para crear una nueva organizacion
  create(organizacion: Partial<Organizacion>): Observable<Organizacion> {
    return this.http.post<Organizacion>(this.baseUrl, organizacion);
  }

  // metodo para crear una actualizar una organizacion
  update(id: number, organizacion: Organizacion): Observable<Organizacion> {
    return this.http.put<Organizacion>(`${this.baseUrl}/${id}`, organizacion);
  }

  // metodo para eliminar una organizacion
  delete(id: number): Observable<void> {
    return this.http.delete<void>(`${this.baseUrl}/${id}`);
  }
}
