import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';
import { Venta, VentaCreateDto } from '../interfaces/venta';

@Injectable({ providedIn: 'root' })
export class VentasService {
  private readonly baseUrl = `${environment.apiUrl}/api/ventas`;

  constructor(private http: HttpClient) {}

  // Filtra por organización si se pasa el id.
  getAll(organizacionId?: number): Observable<Venta[]> {
    const params = organizacionId
      ? new HttpParams().set('organizacionId', organizacionId)
      : undefined;
    return this.http.get<Venta[]>(this.baseUrl, { params });
  }

  getById(id: number): Observable<Venta> {
    return this.http.get<Venta>(`${this.baseUrl}/${id}`);
  }

  create(dto: VentaCreateDto): Observable<Venta> {
    return this.http.post<Venta>(this.baseUrl, dto);
  }
}