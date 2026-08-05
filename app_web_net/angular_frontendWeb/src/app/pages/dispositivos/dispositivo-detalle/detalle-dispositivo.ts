import { Component, OnInit } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { DatePipe } from '@angular/common';

import { DispositivosService } from '../../../services/dispositivos';
import { Dispositivo } from '../../../interfaces/dispositivo';

@Component({
  selector: 'app-dispositivo-detalle',
  standalone: true,
  imports: [
    DatePipe
  ],
  templateUrl: './detalle-dispositivo.html',
  styleUrl: './detalle-dispositivo.css',
})
export class DispositivoDetalle implements OnInit {

  dispositivo: Dispositivo | null = null;

  cargando = true;

  error = false;

  eliminando = false;

  mostrarModalEliminar = false;


  constructor(
    private route: ActivatedRoute,
    private router: Router,
    private dispositivosService: DispositivosService
  ){}


  ngOnInit(): void {

    const id = Number(
      this.route.snapshot.paramMap.get('id')
    );

    if(!id){

      this.error = true;
      this.cargando = false;

      return;

    }

    this.cargarDispositivo(id);

  }



  cargarDispositivo(id:number):void{

    this.cargando = true;
    this.error = false;


    this.dispositivosService.getById(id)
    .subscribe({

      next:(data)=>{

        console.log(
          'DISPOSITIVO DETALLE:',
          data
        );


        this.dispositivo = data;

        this.cargando = false;

      },


      error:(err)=>{

        console.error(
          'Error al cargar dispositivo:',
          err
        );


        this.error = true;

        this.cargando = false;

      }

    });

  }



  editar():void{

    if(!this.dispositivo){

      return;

    }


    this.router.navigate([
      '/dispositivos',
      this.dispositivo.id,
      'editar'
    ]);

  }



  cancelar():void{

    this.router.navigate([
      '/dispositivos'
    ]);

  }



  abrirModalEliminar():void{

    this.mostrarModalEliminar = true;

  }



  cerrarModalEliminar():void{

    this.mostrarModalEliminar = false;

  }



  eliminar():void{

    if(!this.dispositivo){

      return;

    }


    this.eliminando = true;


    this.dispositivosService
    .delete(this.dispositivo.id)
    .subscribe({

      next:()=>{

        this.mostrarModalEliminar = false;

        this.router.navigate([
          '/dispositivos'
        ]);

      },


      error:(err)=>{

        console.error(
          'Error al eliminar:',
          err
        );


        this.eliminando = false;


        alert(
          'No se pudo eliminar el dispositivo'
        );

      }

    });

  }



  formatearId(id:number):string{

    return id
      .toString()
      .padStart(4,'0');

  }


obtenerOrganizacion(): string {

  if (!this.dispositivo?.organizacion) {
    return 'Sin organización';
  }

  return this.dispositivo.organizacion;

}

}
