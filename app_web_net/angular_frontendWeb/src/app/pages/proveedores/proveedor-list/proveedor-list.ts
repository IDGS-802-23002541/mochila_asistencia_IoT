import { Component } from '@angular/core';
import { RouterLink } from '@angular/router';
import { ProveedorResumen } from '../../../interfaces/proveedor';

@Component({
  selector: 'app-proveedor-list',
  standalone: true,
  imports: [RouterLink],
  templateUrl: './proveedor-list.html',
  styleUrl: './proveedor-list.css',
})
export class ProveedorList {
  // TODO: reemplazar por datos reales del servicio
  cargando = false;
  error = false;

  proveedores: ProveedorResumen[] = [
    { id: 1, nombre: 'Distribuidora Industrial del Bajío', estado_Activo: true },
    { id: 2, nombre: 'Suministros Eléctricos SA', estado_Activo: true },
    { id: 3, nombre: 'Componentes IoT MX', estado_Activo: false },
    { id: 4, nombre: 'Electronica de León', estado_Activo: true }
  ];

  cargarProveedores(): void {
    // TODO: conectar con el servicio
  }
}
