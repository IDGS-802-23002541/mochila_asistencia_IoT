import { Component } from '@angular/core';
import { Router } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { Sidebar } from '../../../sidebar/sidebar';
import { DispositivosService } from '../../../services/dispositivos';

@Component({
  selector: 'app-nuevo-dispositivo',
  standalone: true,
  imports: [
    FormsModule,
    Sidebar
  ],
  templateUrl: './nuevo-dispositivo.html',
  styleUrl: './nuevo-dispositivo.css',
})
export class NuevoDispositivo {

  dispositivo = {
    organizacionId: 1,
    macAddress: '',
    estado: 'Activo'
  };

  guardando = false;
  error = '';

  constructor(
    private dispositivosService: DispositivosService,
    private router: Router
  ) {}


  guardar(): void {

    this.error = '';

    if (!this.dispositivo.macAddress) {

      this.error = 'La MAC Address es obligatoria';
      return;

    }


    this.guardando = true;


    this.dispositivosService.create(this.dispositivo)
      .subscribe({

        next: () => {

          this.router.navigate(['/dispositivos']);

        },

        error: (err) => {

          console.error(
            'Error al crear dispositivo',
            err
          );

          this.error =
            'No se pudo crear el dispositivo';

          this.guardando = false;

        }

      });

  }


  cancelar(): void {

    this.router.navigate(['/dispositivos']);

  }

}