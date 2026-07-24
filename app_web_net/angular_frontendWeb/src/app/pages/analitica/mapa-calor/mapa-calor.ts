import { AfterViewInit, Component, OnDestroy, OnInit } from '@angular/core';
import { FormsModule } from '@angular/forms';
import * as L from 'leaflet';
import 'leaflet.heat';

@Component({
  selector:'app-mapa-calor',
  standalone:true,
  imports:[FormsModule],
  templateUrl:'./mapa-calor.html',
  styleUrl:'./mapa-calor.css'
})
export class MapaCalor implements AfterViewInit, OnDestroy, OnInit{
  private map!:L.Map;
  private capaCalor:any;
  mostrarFiltros=false;
  filtroZona='';
  filtroRiesgo='';
  eventosFiltrados:any[]=[];
  zonasCriticas=0;
  dispositivosActivos=10;

  private readonly CENTRO_UTL:L.LatLngExpression=[
    21.0629,
    -101.5815
  ];

  private datosMock=[
    {lat:21.06419,lon:-101.584016,peso:9},
    {lat:21.062353,lon:-101.579416,peso:7},
    {lat:21.062636,lon:-101.578256,peso:8},
    {lat:21.06262,lon:-101.581889,peso:10},
    {lat:21.063279,lon:-101.57953,peso:5},
    {lat:21.063498,lon:-101.580792,peso:6},
    {lat:21.064189,lon:-101.58293,peso:4},
    {lat:21.063788,lon:-101.581147,peso:5},
    {lat:21.063645,lon:-101.580767,peso:3},
    {lat:21.063462,lon:-101.580336,peso:4},
    {lat:21.062876,lon:-101.578665,peso:6},
    {lat:21.06385,lon:-101.581707,peso:5},
    {lat:21.063523,lon:-101.582475,peso:4},
    {lat:21.06297,lon:-101.581861,peso:7}
  ];

  ngOnInit():void{
    this.eventosFiltrados=this.datosMock;
    this.calcularDatos();
  }

  ngAfterViewInit():void{
    setTimeout(()=>{
      this.iniciarMapa();
      this.pintarMapaCalor();
      this.map.invalidateSize();
    },300);
  }

  private iniciarMapa():void{
    this.map=L.map('mapa-calor',{
      center:this.CENTRO_UTL,
      zoom:17
    });

    L.tileLayer(
      'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
      {
        attribution:'© OpenStreetMap contributors',
        maxZoom:19
      }
    ).addTo(this.map);

    fetch('assets/utl-campus.geojson')
    .then(response=>{
      if(!response.ok){
        throw new Error('No se encontró el archivo GeoJSON');
      }
      return response.json();
    })
    .then(data=>{
      const campus=L.geoJSON(data,{
        style:{
          color:'#2563eb',
          weight:2,
          fillOpacity:.15
        }
      }).addTo(this.map);

      this.map.fitBounds(campus.getBounds());
    })
    .catch(error=>{
      console.error('Error cargando GeoJSON:',error);
    });
  }

  private pintarMapaCalor():void{
    if(this.capaCalor){
      this.map.removeLayer(this.capaCalor);
    }

    const puntos:[number,number,number][]=
    this.eventosFiltrados.map(punto=>[
      punto.lat,
      punto.lon,
      punto.peso
    ]);

    this.capaCalor=(L as any).heatLayer(
      puntos,
      {
        radius:35,
        blur:25,
        maxZoom:17,
        gradient:{
          0.2:'blue',
          0.5:'lime',
          0.8:'orange',
          1:'red'
        }
      }
    ).addTo(this.map);
  }

  aplicarFiltros():void{
    this.eventosFiltrados=this.datosMock.filter(evento=>{
      let cumple=true;

      if(this.filtroRiesgo==='Alto'){
        cumple=evento.peso>=8;
      }

      if(this.filtroRiesgo==='Medio'){
        cumple=evento.peso>=5 && evento.peso<8;
      }

      if(this.filtroRiesgo==='Bajo'){
        cumple=evento.peso<5;
      }

      return cumple;
    });

    this.calcularDatos();
    this.pintarMapaCalor();
  }

  limpiarFiltros():void{
    this.filtroZona='';
    this.filtroRiesgo='';
    this.eventosFiltrados=this.datosMock;
    this.calcularDatos();
    this.pintarMapaCalor();
  }

  calcularDatos():void{
    this.zonasCriticas=this.eventosFiltrados.filter(
      evento=>evento.peso>=8
    ).length;
  }

  ngOnDestroy():void{
    if(this.map){
      this.map.remove();
    }
  }
}