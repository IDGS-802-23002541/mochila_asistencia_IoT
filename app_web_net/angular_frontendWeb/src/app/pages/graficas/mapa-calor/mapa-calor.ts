import { AfterViewInit, Component, Input, OnChanges, OnDestroy, SimpleChanges } from '@angular/core';
import * as L from 'leaflet';
import 'leaflet.heat';
import { ZonaAccesibilidad } from '../models/zona-accesibilidad.model';

@Component({
  selector: 'app-mapa-calor',
  standalone: true,
  imports: [],
  templateUrl: './mapa-calor.html',
  styleUrl: './mapa-calor.css',
})
export class MapaCalor implements AfterViewInit, OnChanges, OnDestroy {
  // Ya no hace fetch propio -- recibe las zonas del padre (Graficas),
  // igual que grafica-iaz / grafica-desglose / interpretacion, para no
  // duplicar llamadas al API.
  @Input({ required: true }) zonas: ZonaAccesibilidad[] = [];

  private map!: L.Map;
  private heatLayer?: L.Layer;
  private mapaListo = false;

  // Centro real del geojson (~21.0637, -101.5817). fitBounds() recentra
  // igual, pero se corrige para no dejar dato muerto (hallazgo colateral,
  // ticket 002).
  private readonly CENTRO_UTL: L.LatLngExpression = [21.0637, -101.5817];

  ngAfterViewInit(): void {
    this.iniciarMapa();
    this.mapaListo = true;
    // Si las zonas ya llegaron antes de que el mapa terminara de montarse
    // (poco probable, pero por si acaso), pintar de una vez.
    if (this.zonas.length) this.pintarMapaCalor();
  }

  ngOnChanges(changes: SimpleChanges): void {
    // El fetch del padre es asincrono -- zonas puede llegar DESPUES de
    // ngAfterViewInit. Aqui se (re)pinta el heatmap cada vez que zonas
    // cambia, siempre que el mapa ya este listo.
    if (changes['zonas'] && this.mapaListo && this.zonas.length) {
      this.pintarMapaCalor();
    }
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
    // Si ya habia una capa de calor pintada (ej. zonas se actualizo de
    // nuevo), se quita antes de pintar la nueva -- evita capas
    // duplicadas encimadas.
    if (this.heatLayer) {
      this.map.removeLayer(this.heatLayer);
    }
    // Peso del heatmap = IAZ real de cada zona.
    const puntos: [number, number, number][] = this.zonas.map((z) => [
      z.lat,
      z.lon,
      z.iaz,
    ]);
    this.heatLayer = (L as any)
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
