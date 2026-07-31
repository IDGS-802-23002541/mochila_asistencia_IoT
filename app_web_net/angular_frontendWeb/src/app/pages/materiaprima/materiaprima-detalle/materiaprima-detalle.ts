import { Component } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { MateriaPrima } from '../../../interfaces/materiaprima';

@Component({
  selector: 'app-materiaprima-detalle',
  standalone: true,
  imports: [],
  templateUrl: './materiaprima-detalle.html',
  styleUrl: './materiaprima-detalle.css',
})
export class MateriaPrimaDetalle {
  // TODO: reemplazar por datos reales del servicio, cargados según route.snapshot.paramMap
  cargando = false;
  error = false;
  eliminando = false;

  registro: MateriaPrima | null = {
    id: 1,
    nombre: 'Placa de acero inoxidable',
    estado_Activo: true,
    categoria: '—',
    unidad_Medida: '—',
    stock_Actual: '—',
    precio_Unitario: '—',
    proveedor: '—',
  };

  constructor(private route: ActivatedRoute, private router: Router) {}

  editar(): void {
    if (!this.registro) return;
    this.router.navigate(['/materiaprima', this.registro.id, 'editar']);
  }

  eliminar(): void {
    // TODO: conectar con el servicio para eliminar el registro
  }

  formatearId(id: number): string {
    return id.toString().padStart(4, '0');
  }
}
