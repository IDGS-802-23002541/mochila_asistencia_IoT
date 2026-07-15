import { Component, Input } from '@angular/core';
import { ZonaAccesibilidad } from '../graficas/models/zona-accesibilidad.model';

@Component({
  selector: 'app-interpretacion',
  standalone: true,
  imports: [],
  templateUrl: './interpretacion.html',
  styleUrl: './interpretacion.css',
})
export class Interpretacion {
  @Input({ required: true }) zonas: ZonaAccesibilidad[] = [];

  get zonaMasCritica(): ZonaAccesibilidad {
    return [...this.zonas].sort((a, b) => b.iaz - a.iaz)[0];
  }

  get zonaMasSegura(): ZonaAccesibilidad {
    return [...this.zonas].sort((a, b) => a.iaz - b.iaz)[0];
  }

  get iazPromedio(): string {
    const suma = this.zonas.reduce((acc, z) => acc + z.iaz, 0);
    return (suma / this.zonas.length).toFixed(2);
  }

  get totalEventos(): number {
    return this.zonas.reduce((acc, z) => acc + z.cantidadEventos, 0);
  }

  get totalZonas(): number {
    return this.zonas.length;
  }
}
