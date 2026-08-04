import { Component, OnInit, signal } from '@angular/core';
import { MapaCalor } from './mapa-calor/mapa-calor';
import { GraficaIaz } from './grafica-iaz/grafica-iaz';
import { GraficaDesglose } from './grafica-desglose/grafica-desglose';
import { Interpretacion } from './interpretacion/interpretacion';
import { ZonaAccesibilidad } from './models/zona-accesibilidad.model';
import { API_BASE_URL } from './config/api.config';

@Component({
  selector: 'app-graficas',
  standalone: true,
  imports: [MapaCalor, GraficaIaz, GraficaDesglose, Interpretacion],
  templateUrl: './graficas.html',
  styleUrl: './graficas.css',
})
export class Graficas implements OnInit {
  // FIX: este proyecto no usa zone.js (Angular zoneless, confirmado por
  // ausencia de "zone.js" en package.json). Sin zone.js, Angular NO
  // detecta automaticamente cuando una propiedad normal cambia dentro de
  // un await/fetch -- hay que usar un signal para que la vista se
  // actualice sola cuando llega el dato real.
  zonas = signal<ZonaAccesibilidad[]>([]);

  async ngOnInit(): Promise<void> {
    try {
      const res = await fetch(`${API_BASE_URL}/api/zonas/accesibilidad`);
      const data = await res.json();
      this.zonas.set(data);
    } catch (err) {
      console.error('Error cargando zonas desde el API:', err);
      this.zonas.set([]);
    }
  }
}
