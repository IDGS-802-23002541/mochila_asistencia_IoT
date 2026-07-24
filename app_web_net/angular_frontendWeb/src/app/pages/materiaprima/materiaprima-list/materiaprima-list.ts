import { Component } from '@angular/core';
import { RouterLink } from '@angular/router';
import { MateriaPrimaResumen } from '../../../interfaces/materiaprima';

@Component({
  selector: 'app-materiaprima-list',
  standalone: true,
  imports: [RouterLink],
  templateUrl: './materiaprima-list.html',
  styleUrl: './materiaprima-list.css',
})
export class MateriaPrimaList {
  // TODO: reemplazar por datos reales del servicio
  cargando = false;
  error = false;

  materiaprima: MateriaPrimaResumen[] = [
    { id: 1, nombre: 'Placa de acero inoxidable', estado_Activo: true },
    { id: 2, nombre: 'Sensor ultrasónico HC-SR04', estado_Activo: true },
    { id: 3, nombre: 'Cable UTP Cat 6', estado_Activo: true },
    { id: 4, nombre: 'Batería Li-Ion 18650', estado_Activo: false }
  ];

  cargarMateriaPrima(): void {
    // TODO: conectar con el servicio
  }
}
