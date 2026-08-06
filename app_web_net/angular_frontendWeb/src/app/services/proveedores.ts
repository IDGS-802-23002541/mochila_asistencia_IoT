import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable, of, tap } from 'rxjs';
import { Proveedor } from '../interfaces/proveedor';
import { environment } from '../../environments/environment';

@Injectable({
  providedIn: 'root',
})
export class ProveedoresService {

  private readonly baseUrl =
    `${environment.apiUrl}/api/proveedores`;

  private proveedoresCache: Proveedor[] = [];

  constructor(private http: HttpClient) {}

  getAll(): Observable<Proveedor[]> {

    if (this.proveedoresCache.length > 0) {
      return of(this.proveedoresCache);
    }

    return this.http.get<Proveedor[]>(this.baseUrl)
      .pipe(
        tap(data => {
          this.proveedoresCache = data;
        })
      );
  }

  getById(id: number): Observable<Proveedor> {

    const encontrado = this.proveedoresCache.find(
      p => p.idProveedor === id
    );

    if (encontrado) {
      return of(encontrado);
    }

    return this.http.get<Proveedor>(
      `${this.baseUrl}/${id}`
    )
    .pipe(
      tap(data => {
        this.actualizarCache(data);
      })
    );
  }

  create(proveedor: Partial<Proveedor>): Observable<Proveedor> {

    return this.http.post<Proveedor>(
      this.baseUrl,
      proveedor
    )
    .pipe(
      tap(nuevo => {
        this.proveedoresCache.push(nuevo);
      })
    );
  }

  update(
    id: number,
    proveedor: Partial<Proveedor>
  ): Observable<Proveedor> {

    return this.http.put<Proveedor>(
      `${this.baseUrl}/${id}`,
      proveedor
    )
    .pipe(
      tap(actualizado => {

        const index =
          this.proveedoresCache.findIndex(
            p => p.idProveedor === id
          );

        if (index !== -1) {
          this.proveedoresCache[index] = actualizado;
        }

      })
    );
  }

  delete(id: number): Observable<void> {

    return this.http.delete<void>(
      `${this.baseUrl}/${id}`
    )
    .pipe(
      tap(() => {

        this.proveedoresCache =
          this.proveedoresCache.filter(
            p => p.idProveedor !== id
          );

      })
    );

  }

  limpiarCache() {
    this.proveedoresCache = [];
  }

  private actualizarCache(data: Proveedor) {

    const index =
      this.proveedoresCache.findIndex(
        p => p.idProveedor === data.idProveedor
      );

    if (index >= 0) {
      this.proveedoresCache[index] = data;
    } else {
      this.proveedoresCache.push(data);
    }

  }

}
