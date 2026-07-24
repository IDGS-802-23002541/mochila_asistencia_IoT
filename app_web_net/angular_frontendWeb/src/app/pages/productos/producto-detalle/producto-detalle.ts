import { Component } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { Producto } from '../../../interfaces/producto';

@Component({
  selector: 'app-producto-detalle',
  standalone: true,
  imports: [],
  templateUrl: './producto-detalle.html',
  styleUrl: './producto-detalle.css',
})
export class ProductoDetalle {
  // TODO: reemplazar por datos reales del servicio, cargados según route.snapshot.paramMap
  cargando = false;
  error = false;
  eliminando = false;

  registro: Producto | null = {
    id: 1,
    nombre: 'Kit Vision Guard Básico',
    estado_Activo: true,
    categoria: '—',
    precio: '—',
    stock: '—',
    descripcion: '—',
  };

  constructor(private route: ActivatedRoute, private router: Router) {}

  editar(): void {
    if (!this.registro) return;
    this.router.navigate(['/productos', this.registro.id, 'editar']);
  }

  eliminar(): void {
    // TODO: conectar con el servicio para eliminar el registro
  }

  formatearId(id: number): string {
    return id.toString().padStart(4, '0');
  }
}
