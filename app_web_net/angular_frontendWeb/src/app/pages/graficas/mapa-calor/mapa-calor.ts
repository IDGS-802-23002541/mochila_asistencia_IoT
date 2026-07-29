import { AfterViewInit, Component, OnDestroy } from '@angular/core';
import * as L from 'leaflet';
import 'leaflet.heat';
import { ZonaAccesibilidad } from '../models/zona-accesibilidad.model';
import { ZONAS_MOCK } from '../data/zonas-mock';

@Component({
  selector: 'app-mapa-calor',
  standalone: true,
  imports: [],
  templateUrl: './mapa-calor.html',
  styleUrl: './mapa-calor.css',
})
export class MapaCalor implements AfterViewInit, OnDestroy {
  private map!: L.Map;
  // FIX: centro del geojson real (~21.0637, -101.5817), no el valor viejo
  // desalineado que traia el componente (hallazgo colateral, ticket 002).
  // fitBounds() recentra igual, pero se corrige para no dejar dato muerto.
  private readonly CENTRO_UTL: L.LatLngExpression = [21.0637, -101.5817];

  // FIX: se quita el mock aislado (datosMock con 'peso' arbitrario, sin
  // relacion con el resto del modulo de graficas). Ahora consume
  // ZonaAccesibilidad, igual que grafica-iaz / grafica-desglose /
  // interpretacion. TODO: reemplazar ZONAS_MOCK por fetch() a un
  // endpoint real cuando el backend/Danna lo exponga; mientras tanto
  // usa el mismo mock compartido del modulo.
  private zonas: ZonaAccesibilidad[] = ZONAS_MOCK;

  ngAfterViewInit(): void {
    this.iniciarMapa();
    this.pintarMapaCalor();
  }

  private iniciarMapa(): void {
    this.map = L.map('mapa-calor').setView(this.CENTRO_UTL, 17);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: '© OpenStreetMap contributors',
      maxZoom: 19,
    }).addTo(this.map);

    fetch('utl-campus.geojson')
      .then((res) => res.json())
      .then((data) => {
        const capa = L.geoJSON(data, {
          style: { color: '#2563eb', weight: 2, fillOpacity: 0.1 },
        }).addTo(this.map);
        this.map.fitBounds(capa.getBounds());
      })
      .catch((err) => console.error('Error cargando geojson:', err));
  }

  private pintarMapaCalor(): void {
    // El peso del heatmap ahora es el IAZ real de cada zona (entre mas
    // alto el IAZ, mas caliente se ve la zona), en vez del 'peso'
    // arbitrario que traia el mock viejo.
    const puntos: [number, number, number][] = this.zonas.map((z) => [
      z.lat,
      z.lon,
      z.iaz,
    ]);
    (L as any)
      .heatLayer(puntos, {
        radius: 30,
        blur: 20,
        maxZoom: 17,
        gradient: { 0.2: 'blue', 0.5: 'lime', 0.8: 'orange', 1.0: 'red' },
      })
      .addTo(this.map);
  }

  ngOnDestroy(): void {
    if (this.map) this.map.remove();
  }
}
