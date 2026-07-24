import { Component, inject, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { DispositivosService, Dispositivo } from '../../services/dispositivos';

@Component({
  selector: 'app-dispositivos',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './dispositivos.html',
  styleUrl: './dispositivos.css'
})
export class Dispositivos implements OnInit {
  private servicio = inject(DispositivosService);
  dispositivos: Dispositivo[] = [];
  cargando = true;
  mostrarFormulario = false;
  editando = false;
  error = '';
  mensaje = '';
  dispositivoActual: any = {
    organizacionId: 1,
    macAddress: '',
    estado: 'Activo'
  };
  ngOnInit(): void {
    this.cargar();
  }
  mostrarMensaje(texto: string): void {
    this.mensaje = texto;
    setTimeout(() => {
      this.mensaje = '';
    }, 3000);
  }
  limpiarError(): void {
    setTimeout(() => {
      this.error = '';
    }, 3000);
  }
  cargar(): void {
    this.cargando = true;
    this.servicio.obtenerDispositivos()
      .subscribe({
        next: (data) => {
          this.dispositivos = data;
          this.cargando = false;
        },
        error: (err) => {
          console.error(err);
          this.error = 'No se pudieron cargar los dispositivos';
          this.cargando = false;
          this.limpiarError();
        }
      });
  }
  nuevo(): void {
    this.error = '';
    this.editando = false;
    this.dispositivoActual = {
      organizacionId: 1,
      macAddress: '',
      estado: 'Activo'
    };
    this.mostrarFormulario = true;
  }
  editar(dispositivo: Dispositivo): void {
    this.error = '';
    this.editando = true;
    this.dispositivoActual = {
      id: dispositivo.id,
      organizacionId: dispositivo.organizacionId,
      macAddress: dispositivo.macAddress,
      estado: dispositivo.estado
    };
    this.mostrarFormulario = true;
  }
  guardar(): void {
    this.error = '';
    if (!this.dispositivoActual.macAddress) {
      this.error = 'La MAC Address es obligatoria';
      this.limpiarError();
      return;
    }
    if (this.editando) {
      this.servicio.actualizar(
        this.dispositivoActual.id,
        {
          organizacionId: this.dispositivoActual.organizacionId,
          macAddress: this.dispositivoActual.macAddress,
          estado: this.dispositivoActual.estado
        }
      )
        .subscribe({
          next: (respuesta) => {
            const index = this.dispositivos.findIndex(d => d.id === respuesta.id);
            if (index !== -1) {
              this.dispositivos[index] = respuesta;
            }
            this.mostrarMensaje('Dispositivo actualizado correctamente');
            this.cerrar();
          },
          error: (err) => {
            console.error('ERROR UPDATE:', err);
            this.error = 'No se pudo actualizar el dispositivo';
            this.limpiarError();
          }
        });
    } else {
      const nuevo = {
        organizacionId: this.dispositivoActual.organizacionId,
        macAddress: this.dispositivoActual.macAddress,
        estado: this.dispositivoActual.estado
      };
      this.servicio.crear(nuevo)
        .subscribe({
          next: (respuesta) => {
            this.dispositivos.push(respuesta);
            this.mostrarMensaje('Dispositivo creado correctamente');
            this.cerrar();
          },
          error: (err) => {
            console.error('ERROR CREATE:', err);
            console.log('RESPUESTA API:', err.error);
            this.error = 'No se pudo crear el dispositivo';
            this.limpiarError();
          }
        });
    }
  }
eliminar(id:number):void{
  this.error='';
  if(confirm('¿Deseas eliminar este dispositivo?')){
    this.servicio.eliminar(id)
    .subscribe({
      next:()=>{
        this.dispositivos=this.dispositivos.filter(
          dispositivo=>dispositivo.id!==id
        );
        this.mostrarMensaje('Dispositivo eliminado correctamente');
      },
      error:(err)=>{
        console.error('ERROR DELETE:',err);
        this.error='No se pudo eliminar el dispositivo';
        this.limpiarError();
      }
    });
  }
}
  cerrar(): void {
    this.mostrarFormulario = false;
  }
}