import { Component, inject, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';
import { VentasService } from '../../../services/ventas';
import { SesionService } from '../../../services/sesion';
import { Venta } from '../../../interfaces/venta';

@Component({
  selector: 'app-compras',
  imports: [CommonModule, RouterLink],
  templateUrl: './compras.html',
  styleUrl: './compras.css',
})
export class MisCompras implements OnInit {
  private sesionService = inject(SesionService);
  private ventasService = inject(VentasService);

  cargando = false;
  error = false;
  ventas: Venta[] = [];

  ngOnInit(): void {
    this.cargarCompras();
  }

  cargarCompras(): void {
    this.cargando = true;
    this.error = false;

    const organizacionId = this.sesionService.organizacionId();

    if (!organizacionId) {
      this.error = true;
      this.cargando = false;
      return;
    }

    this.ventasService.getAll(organizacionId).subscribe({
      next: (datos) => {
        this.ventas = datos;
        this.cargando = false;
      },
      error: () => {
        this.error = true;
        this.cargando = false;
      },
    });
  }

  formatearFecha(fecha: string): string {
    const f = new Date(fecha);
    return f.toLocaleDateString('es-MX', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
    });
  }

  formatearMoneda(valor: number): string {
    return new Intl.NumberFormat('es-MX', {
      style: 'currency',
      currency: 'MXN',
    }).format(valor);
  }
}