import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable, of, tap } from 'rxjs';
import { Dispositivo } from '../interfaces/dispositivo';

@Injectable({
  providedIn: 'root',
})
export class DispositivosService {

  private readonly baseUrl =
    'https://lmsidgs902.runasp.net/api/dispositivos';

  private dispositivosCache: Dispositivo[] = [];

  constructor(private http: HttpClient) {}

  getAll(): Observable<Dispositivo[]> {

    if (this.dispositivosCache.length > 0) {
      return of(this.dispositivosCache);
    }

    return this.http.get<Dispositivo[]>(this.baseUrl)
      .pipe(
        tap(data => {
          this.dispositivosCache = data;
        })
      );
  }


  getById(id:number): Observable<Dispositivo> {

    const encontrado = this.dispositivosCache.find(
      d => d.id === id
    );

    if(encontrado){
      return of(encontrado);
    }

    return this.http.get<Dispositivo>(
      `${this.baseUrl}/${id}`
    )
    .pipe(
      tap(data=>{
        this.actualizarCache(data);
      })
    );
  }



  create(dispositivo:Partial<Dispositivo>):Observable<Dispositivo>{

    return this.http.post<Dispositivo>(
      this.baseUrl,
      dispositivo
    )
    .pipe(
      tap(nuevo=>{
        this.dispositivosCache.push(nuevo);
      })
    );
  }



  update(
    id:number,
    dispositivo:Partial<Dispositivo>
  ):Observable<Dispositivo>{

    return this.http.put<Dispositivo>(
      `${this.baseUrl}/${id}`,
      dispositivo
    )
    .pipe(
      tap(actualizado=>{

        const index =
          this.dispositivosCache.findIndex(
            d=>d.id===id
          );

        if(index !== -1){
          this.dispositivosCache[index]=actualizado;
        }

      })
    );
  }



  delete(id:number):Observable<void>{

    return this.http.delete<void>(
      `${this.baseUrl}/${id}`
    )
    .pipe(
      tap(()=>{

        this.dispositivosCache =
        this.dispositivosCache.filter(
          d=>d.id!==id
        );

      })
    );

  }



  limpiarCache(){

    this.dispositivosCache=[];

  }



  private actualizarCache(data:Dispositivo){

    const existe =
      this.dispositivosCache.findIndex(
        d=>d.id===data.id
      );


    if(existe>=0){

      this.dispositivosCache[existe]=data;

    }else{

      this.dispositivosCache.push(data);

    }

  }

}