import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, Router, RouterLink } from '@angular/router';
import { ProductoDetalle as ProductoDetalleModel } from '../../../interfaces/producto';
import { ProductosService } from '../../../services/producto';

@Component({
  selector: 'app-producto-detalle',
  standalone: true,
  imports: [CommonModule, RouterLink],
  templateUrl: './producto-detalle.html',
  styleUrl: './producto-detalle.css',
})
export class ProductoDetalle implements OnInit {
  cargando = false;
  error = false;
  eliminando = false;

  registro: ProductoDetalleModel | null = null;

  constructor(
    private route: ActivatedRoute,
    private router: Router,
    private ProductosService: ProductosService
  ) {}

  ngOnInit(): void {
    const id = Number(this.route.snapshot.paramMap.get('id'));
    this.cargarProducto(id);
  }

  cargarProducto(id: number): void {
    this.cargando = true;
    this.error = false;

    this.ProductosService.getDetalle(id).subscribe({
      next: (data) => {
        this.registro = data;
        this.cargando = false;
      },
      error: () => {
        this.error = true;
        this.cargando = false;
      },
    });
  }

  editar(): void {
    if (!this.registro) return;
    this.router.navigate(['/productos', this.registro.idProducto, 'editar']);
  }

  eliminar(): void {
    if (!this.registro) return;

    this.eliminando = true;
    this.ProductosService.delete(this.registro.idProducto).subscribe({
      next: () => {
        this.router.navigate(['/productos']);
      },
      error: () => {
        this.eliminando = false;
      },
    });
  }

  formatearId(id: number): string {
    return id.toString().padStart(4, '0');
  }
}
