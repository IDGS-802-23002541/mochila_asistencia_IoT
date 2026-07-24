import { Component } from '@angular/core';
import { RouterLink } from '@angular/router';
import { ProductoResumen } from '../../../interfaces/producto';

@Component({
  selector: 'app-producto-list',
  standalone: true,
  imports: [RouterLink],
  templateUrl: './producto-list.html',
  styleUrl: './producto-list.css',
})
export class ProductoList {
  // TODO: reemplazar por datos reales del servicio
  cargando = false;
  error = false;

  productos: ProductoResumen[] = [
    { id: 1, nombre: 'Kit Vision Guard Básico', estado_Activo: true },
    { id: 2, nombre: 'Bastón inteligente V2', estado_Activo: true },
    { id: 3, nombre: 'Pulsera de navegación IoT', estado_Activo: true },
    { id: 4, nombre: 'Módulo de alerta sonora', estado_Activo: false }
  ];

  cargarProductos(): void {
    // TODO: conectar con el servicio
  }
}
