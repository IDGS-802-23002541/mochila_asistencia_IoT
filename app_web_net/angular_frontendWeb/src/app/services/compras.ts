import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';
import { Compra, CompraCreateDto } from '../interfaces/compra';

@Injectable({ providedIn: 'root' })
export class ComprasService {
  private readonly baseUrl = `${environment.apiUrl}/api/compras`;

  constructor(private http: HttpClient) {}

  getAll(): Observable<Compra[]> {
    return this.http.get<Compra[]>(this.baseUrl);
  }

  getById(id: number): Observable<Compra> {
    return this.http.get<Compra>(`${this.baseUrl}/${id}`);
  }

  create(dto: CompraCreateDto): Observable<{ idCompra: number }> {
    return this.http.post<{ idCompra: number }>(this.baseUrl, dto);
  }

  update(id: number, dto: CompraCreateDto): Observable<{ idCompra: number }> {
    return this.http.put<{ idCompra: number }>(`${this.baseUrl}/${id}`, dto);
  }

  delete(id: number): Observable<void> {
    return this.http.delete<void>(`${this.baseUrl}/${id}`);
  }
}