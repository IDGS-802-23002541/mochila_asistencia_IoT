import { Component, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { SesionService } from '../../services/sesion';

@Component({
  selector: 'app-inicio',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './inicio.html',
  styleUrl: './inicio.scss',
})
export class Inicio {

  private sesionService = inject(SesionService);

  usuario = this.sesionService.obtenerNombre() ?? 'Usuario';

}
