import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';

//Me falta checar bien como estan los dispositivos
interface Dispositivo {
  id: number;
  nombre: string;
  tipo: string;
  ubicacion: string;
  estado: 'activo' | 'alerta' | 'inactivo';
  ultimaConexion: string;
}

@Component({
  selector: 'app-dispositivos',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './dispositivos.html',
  styleUrl: './dispositivos.css',
})
export class Dispositivos {

  listaDispositivos: Dispositivo[] = [
    { id: 101, nombre: 'Cámara Perimetral Norte', tipo: 'Sensor de Video', ubicacion: 'Acceso Principal', estado: 'activo', ultimaConexion: 'Hace 2 min' },
    { id: 102, nombre: 'Sensor de Presencia A', tipo: 'Proximidad', ubicacion: 'Almacén Central', estado: 'activo', ultimaConexion: 'Hace 10 seg' },
    { id: 103, nombre: 'Escáner Óptico Industrial', tipo: 'Lector Biométrico', ubicacion: 'Laboratorio de Calidad', estado: 'alerta', ultimaConexion: 'Hace 1 hora' },
    { id: 104, nombre: 'Termómetro de Enfriamiento', tipo: 'Sensor Térmico', ubicacion: 'Cámara Fría 02', estado: 'inactivo', ultimaConexion: 'Ayer, 18:43' },
    { id: 105, nombre: 'Detector de Humo Smart', tipo: 'Seguridad Ambiental', ubicacion: 'Oficinas Administrativas', estado: 'activo', ultimaConexion: 'Hace 5 min' }
  ];

}
