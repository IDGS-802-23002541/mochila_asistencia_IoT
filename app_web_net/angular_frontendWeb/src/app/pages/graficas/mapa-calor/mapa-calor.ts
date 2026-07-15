import { AfterViewInit, Component, OnDestroy } from '@angular/core';
import * as L from 'leaflet';
import 'leaflet.heat'

@Component({
  selector: 'app-mapa-calor',
  standalone: true,
  imports: [],
  templateUrl: './mapa-calor.html',
  styleUrl: './mapa-calor.css',
})
export class MapaCalor implements AfterViewInit, OnDestroy {
  private map!: L.Map;
  private readonly CENTRO_UTL: L.LatLngExpression = [ 21.1092, -101.6275];

 private datosMock = [
  // Estacionamientos — mayor peso (más tránsito/riesgo típico)
  { lat: 21.06419,  lon: -101.584016, peso: 9 },  // Estacionamiento 1
  { lat: 21.062353, lon: -101.579416, peso: 7 },  // Estacionamiento 2
  { lat: 21.062636, lon: -101.578256, peso: 8 },  // Estacionamiento 3

  // Entrada principal — alto tránsito
  { lat: 21.06262,  lon: -101.581889, peso: 10 }, // Entrada

  // Pasillos internos — peso variable
  { lat: 21.063279, lon: -101.57953,  peso: 5 },
  { lat: 21.063498, lon: -101.580792, peso: 6 },
  { lat: 21.064189, lon: -101.58293,  peso: 4 },
  { lat: 21.063788, lon: -101.581147, peso: 5 },
  { lat: 21.063645, lon: -101.580767, peso: 3 },
  { lat: 21.063462, lon: -101.580336, peso: 4 },
  { lat: 21.062876, lon: -101.578665, peso: 6 },
  { lat: 21.06385,  lon: -101.581707, peso: 5 },
  { lat: 21.063523, lon: -101.582475, peso: 4 },
  { lat: 21.06297,  lon: -101.581861, peso: 7 },
];

  ngAfterViewInit(): void{
    this.iniciarMapa();
    this.pintarMapaCalor();
  }

  private iniciarMapa(): void{
    this.map = L.map('mapa-calor').setView(this.CENTRO_UTL,17);
    // mapa base de fondo
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: '© OpenStreetMap contributors',
      maxZoom: 19,
    }).addTo(this.map);
    // geojson del campus encima
    fetch('utl-campus.geojson')
  .then(res => res.json())
  .then(data => {
    const capa = L.geoJSON(data, {
      style: { color: '#2563eb', weight: 2, fillOpacity: 0.1 }
    }).addTo(this.map);
    // Ajusta el zoom/centro automáticamente al contorno real del geojson
      this.map.fitBounds(capa.getBounds());
  }).catch(err => console.error('Error cargando geojson:', err));
  }
  private pintarMapaCalor(): void{
    const puntos: [ number, number, number][] = this.datosMock.map(d => [d.lat, d.lon, d.peso]);
    ( L as any).heatLayer(puntos, {
      radius: 30,
      blur: 20,
      maxZoom: 17,
      gradient:{0.2:'blue', 0.5:'lime', 0.8:'orange',1.0:'red'},
    }).addTo(this.map);
  }

  ngOnDestroy(): void {
    if(this.map) this.map.remove();
  }


}
