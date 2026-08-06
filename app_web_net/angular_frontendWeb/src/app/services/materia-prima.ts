import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import {
  MateriaPrima,
  MateriaPrimaCreateDto,
} from '../interfaces/materiaprima';

@Injectable({ providedIn: 'root' })
export class MateriaPrimaService {
  private baseUrl = '/api/materias-primas';

  constructor(private http: HttpClient) {}

  getAll(): Observable<MateriaPrima[]> {
    return this.http.get<MateriaPrima[]>(this.baseUrl);
  }

  getById(id: number): Observable<MateriaPrima> {
    return this.http.get<MateriaPrima>(`${this.baseUrl}/${id}`);
  }

  create(dto: MateriaPrimaCreateDto): Observable<MateriaPrima> {
    return this.http.post<MateriaPrima>(this.baseUrl, dto);
  }

  update(id: number, dto: MateriaPrimaCreateDto): Observable<MateriaPrima> {
    return this.http.put<MateriaPrima>(`${this.baseUrl}/${id}`, dto);
  }

  delete(id: number): Observable<void> {
    return this.http.delete<void>(`${this.baseUrl}/${id}`);
  }
}
