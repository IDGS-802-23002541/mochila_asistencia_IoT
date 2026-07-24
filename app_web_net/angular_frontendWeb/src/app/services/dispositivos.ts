import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';


export interface Dispositivo {

  id:number;

  organizacionId:number;

  macAddress:string;

  estado:string;

  ultimaConexion:string|null;

  fechaRegistro:string;

  organizacion:string|null;

}



@Injectable({
  providedIn:'root'
})
export class DispositivosService {


  private http=inject(HttpClient);


  private apiUrl=
  'https://lmsidgs902.runasp.net/api/dispositivos';



  obtenerDispositivos():Observable<Dispositivo[]>{

    return this.http.get<Dispositivo[]>(
      this.apiUrl
    );

  }



  crear(dispositivo:any){

    return this.http.post<Dispositivo>(
      this.apiUrl,
      dispositivo
    );

  }



  actualizar(id:number,dispositivo:any){

    return this.http.put<Dispositivo>(
      `${this.apiUrl}/${id}`,
      dispositivo
    );

  }



  eliminar(id:number){

    return this.http.delete(
      `${this.apiUrl}/${id}`
    );

  }


}