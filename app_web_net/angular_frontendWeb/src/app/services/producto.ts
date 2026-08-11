import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';
import {
  Producto,
  ProductoResumen,
  ProductoDetalle,
  ProductoCreateDto,
  ProductoPublico,
  DocumentoCreateDto,
  ContenidoItem,
} from '../interfaces/producto';

@Injectable({ providedIn: 'root' })
export class ProductosService {
  private readonly baseUrl = `${environment.apiUrl}/api/productos`;

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

  // Detalle visible para el cliente: sin receta, costos ni stock.
  getPublico(id: number): Observable<ProductoPublico> {
    return this.http.get<ProductoPublico>(`${this.baseUrl}/publico/${id}`);
  }

  // Guias y manuales (base64)
  descargarDocumento(idDocumento: number): Observable<{
    idProductoDocumento: number;
    nombreArchivo: string;
    tipoContenido: string;
    contenidoBase64: string;
  }> {
    return this.http.get<{
      idProductoDocumento: number;
      nombreArchivo: string;
      tipoContenido: string;
      contenidoBase64: string;
    }>(`${this.baseUrl}/documentos/${idDocumento}`);
  }

  agregarDocumento(id: number, dto: DocumentoCreateDto): Observable<{ idProductoDocumento: number }> {
    return this.http.post<{ idProductoDocumento: number }>(
      `${this.baseUrl}/${id}/documentos`,
      dto
    );
  }

  eliminarDocumento(idDocumento: number): Observable<void> {
    return this.http.delete<void>(`${this.baseUrl}/documentos/${idDocumento}`);
  }

  // Extras del paquete
  agregarContenido(id: number, dto: ContenidoItem): Observable<any> {
    return this.http.post<any>(`${this.baseUrl}/${id}/contenido`, dto);
  }

  eliminarContenido(id: number, idContenido: number): Observable<void> {
    return this.http.delete<void>(`${this.baseUrl}/${id}/contenido/${idContenido}`);
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
