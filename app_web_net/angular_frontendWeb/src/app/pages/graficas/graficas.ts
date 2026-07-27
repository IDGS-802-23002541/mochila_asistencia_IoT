import { Component } from '@angular/core';
import { MapaCalor } from './mapa-calor/mapa-calor';
import { GraficaIaz } from './grafica-iaz/grafica-iaz';
import { GraficaDesglose } from './grafica-desglose/grafica-desglose';
import { Interpretacion } from './interpretacion/interpretacion';
import { ZONAS_MOCK } from './data/zonas-mock';
import { ZonaAccesibilidad } from './models/zona-accesibilidad.model';

@Component({
  selector: 'app-graficas',
  standalone: true,
  imports: [MapaCalor, GraficaIaz, GraficaDesglose, Interpretacion],
  templateUrl: './graficas.html',
  styleUrl: './graficas.css',
})
export class Graficas {
  zonas: ZonaAccesibilidad[] = ZONAS_MOCK;
}
