import { Component, OnInit } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { DispositivosService } from '../../../services/dispositivos';
import { Dispositivo } from '../../../interfaces/dispositivo';

@Component({
  selector: 'app-editar-dispositivo',
  standalone: true,
  imports: [
    FormsModule
  ],
  templateUrl: './editar-dispositivo.html',
  styleUrl: './editar-dispositivo.css',
})
export class EditarDispositivo implements OnInit {

  dispositivo: Dispositivo = {
    id: 0,
    organizacionId: 0,
    macAddress: '',
    estado: 'Activo',
    ultimaConexion: null,
    fechaRegistro: '',
    organizacion: null
  };

  guardando = false;
  error = '';

  constructor(
    private route: ActivatedRoute,
    private router: Router,
    private dispositivosService: DispositivosService
  ) {}

  ngOnInit(): void {

    const id = Number(
      this.route.snapshot.paramMap.get('id')
    );

    if(id){

      this.cargar(id);

    }else{

      this.error = 'ID de dispositivo inválido';

    }

  }


  cargar(id:number):void {

    this.dispositivosService
    .getById(id)
    .subscribe({

      next:(data)=>{

        this.dispositivo = data;

      },

      error:(err)=>{

        console.error(
          'Error al cargar dispositivo',
          err
        );

        this.error =
        'No se pudo cargar el dispositivo';

      }

    });

  }


  guardar():void {

    this.error = '';

    this.guardando = true;


    const datos = {

      organizacionId:
      this.dispositivo.organizacionId,

      macAddress:
      this.dispositivo.macAddress,

      estado:
      this.dispositivo.estado

    };


    this.dispositivosService
    .update(
      this.dispositivo.id,
      datos
    )
    .subscribe({

      next:(data)=>{

        console.log(
          'Dispositivo actualizado',
          data
        );

        this.router.navigate([
          '/dispositivos'
        ]);

      },

      error:(err)=>{

        console.error(
          'Error al actualizar dispositivo',
          err
        );

        this.error =
        'No se pudo actualizar el dispositivo';

        this.guardando = false;

      }

    });

  }


  cancelar():void {

    this.router.navigate([
      '/dispositivos'
    ]);

  }

}
