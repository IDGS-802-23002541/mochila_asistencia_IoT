import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RouterLink } from '@angular/router';
import { MateriaPrima } from '../../../interfaces/materiaprima';
import { Proveedor } from '../../../interfaces/proveedor';
import { CompraCreateDto } from '../../../interfaces/compra';
import { MateriaPrimaService } from '../../../services/materia-prima';
import { ProveedoresService } from '../../../services/proveedores';
import { ComprasService } from '../../../services/compras';

@Component({
  selector: 'app-materiaprima-list',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterLink],
  templateUrl: './materiaprima-list.html',
  styleUrl: './materiaprima-list.css',
})
export class MateriaPrimaList implements OnInit {
  cargando = false;
  error = false;

  materiaprima: MateriaPrima[] = [];

  // --- Modal de compra ---
  modalAbierto = false;
  guardando = false;
  errorCompra = '';

  itemSeleccionado: MateriaPrima | null = null;
  proveedores: Proveedor[] = [];
  proveedorSeleccionado = 0;
  cantidadCompra = 1;
  precioCompra = 0;

  constructor(
    private materiaPrimaService: MateriaPrimaService,
    private proveedoresService: ProveedoresService,
    private comprasService: ComprasService
  ) {}

  ngOnInit(): void {
    this.cargarMateriaPrima();
    this.cargarProveedores();
  }

  cargarMateriaPrima(): void {
    this.cargando = true;
    this.error = false;

    this.materiaPrimaService.getAll().subscribe({
      next: (datos) => {
        this.materiaprima = datos;
        this.cargando = false;
      },
      error: () => {
        this.error = true;
        this.cargando = false;
      },
    });
  }

  cargarProveedores(): void {
    this.proveedoresService.getAll().subscribe({
      next: (datos) => {
        this.proveedores = datos;
      },
      error: () => {
        this.proveedores = [];
      },
    });
  }

  stockBajo(item: MateriaPrima): boolean {
    return item.stock <= item.stockMinimo;
  }

  precioPromedio(item: MateriaPrima): number {
    return item.precioPromedio ?? item.costoUnitario;
  }

  // --- Modal de compra ---
  abrirCompra(item: MateriaPrima): void {
    this.itemSeleccionado = item;
    this.proveedorSeleccionado = item.idProveedor;
    this.cantidadCompra = 1;
    this.precioCompra = item.precioPromedio ?? item.costoUnitario;
    this.errorCompra = '';
    this.modalAbierto = true;
  }

  cerrarModal(): void {
    this.modalAbierto = false;
    this.itemSeleccionado = null;
  }

  totalCompra(): number {
    return this.cantidadCompra * this.precioCompra;
  }

  comprar(): void {
    if (!this.itemSeleccionado) return;

    if (this.cantidadCompra <= 0) {
      this.errorCompra = 'La cantidad debe ser mayor a 0.';
      return;
    }
    if (this.precioCompra < 0) {
      this.errorCompra = 'El precio no puede ser negativo.';
      return;
    }

    const dto: CompraCreateDto = {
      idProveedor: this.proveedorSeleccionado,
      detalles: [
        {
          idMateriaPrima: this.itemSeleccionado.idMateriaPrima,
          cantidad: this.cantidadCompra,
          precioUnitario: this.precioCompra,
        },
      ],
    };

    this.guardando = true;
    this.errorCompra = '';

    this.comprasService.create(dto).subscribe({
      next: () => {
        this.guardando = false;
        this.cerrarModal();
        this.cargarMateriaPrima();
      },
      error: (err) => {
        this.guardando = false;
        this.errorCompra =
          err?.error?.error ?? 'No se pudo registrar la compra. Intenta de nuevo.';
      },
    });
  }
}
