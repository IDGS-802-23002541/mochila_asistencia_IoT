import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { DispositivosService } from '../../../services/dispositivos';
import { OrganizacionesService } from '../../../services/organizaciones';
import { Organizacion } from '../../../interfaces/organizacion';

@Component({
  selector: 'app-nuevo-dispositivo',
  standalone: true,
  imports: [
    FormsModule
  ],
  templateUrl: './nuevo-dispositivo.html',
  styleUrl: './nuevo-dispositivo.css',
})
export class NuevoDispositivo implements OnInit {

  dispositivo = {
    organizacionId: 0,
    macAddress: '',
    estado: 'Activo'
  };

  organizaciones: Organizacion[] = [];

  guardando = false;
  error = '';

  constructor(
    private dispositivosService: DispositivosService,
    private organizacionesService: OrganizacionesService,
    private router: Router
  ) {}

  ngOnInit(): void {
    this.cargarOrganizaciones();
  }

  cargarOrganizaciones(): void {
    this.organizacionesService.getAll().subscribe({
      next: (datos) => {
        this.organizaciones = datos;
      },
      error: () => {
        this.organizaciones = [];
      },
    });
  }


  guardar(): void {

    this.error = '';

    if (!this.dispositivo.macAddress) {

      this.error = 'La MAC Address es obligatoria';
      return;

    }

    if (!this.dispositivo.organizacionId) {

      this.error = 'Selecciona una organización';
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
