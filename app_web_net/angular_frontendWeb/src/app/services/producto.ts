import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';
import {
  Producto,
  ProductoResumen,
  ProductoDetalle,
  ProductoCreateDto,
} from '../interfaces/producto';

@Injectable({ providedIn: 'root' })
export class ProductosService {
  private baseUrl = `${environment.apiUrl}/api/productos`;

  constructor(private http: HttpClient) {}

  getAll(): Observable<ProductoResumen[]> {
    return this.http.get<ProductoResumen[]>(this.baseUrl);
  }

  getById(id: number): Observable<Producto> {
    return this.http.get<Producto>(`${this.baseUrl}/${id}`);
  }

  // Producto + receta (nombre de cada materia prima y cantidad en piezas).
  getDetalle(id: number): Observable<ProductoDetalle> {
    return this.http.get<ProductoDetalle>(`${this.baseUrl}/${id}/detalle`);
  }

  // Crea el producto junto con su receta en una sola llamada.
  create(dto: ProductoCreateDto): Observable<{ idProducto: number }> {
    return this.http.post<{ idProducto: number }>(this.baseUrl, dto);
  }

  // Actualiza datos + reemplaza la receta completa.
  update(id: number, dto: ProductoCreateDto): Observable<{ idProducto: number }> {
    return this.http.put<{ idProducto: number }>(`${this.baseUrl}/${id}`, dto);
  }

  delete(id: number): Observable<void> {
    return this.http.delete<void>(`${this.baseUrl}/${id}`);
  }
}
