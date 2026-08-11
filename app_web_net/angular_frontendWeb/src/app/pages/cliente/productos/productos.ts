import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, Router } from '@angular/router';
import { ProductosService } from '../../../services/producto';
import { ProductoPublico } from '../../../interfaces/producto';

@Component({
  selector: 'app-productos',
  imports: [CommonModule],
  templateUrl: './productos.html',
  styleUrl: './productos.css',
})
export class MisProductos implements OnInit {
  cargando = false;
  error = false;
  producto: ProductoPublico | null = null;
  descargandoId: number | null = null;
  errorDescarga = '';

  constructor(
    private route: ActivatedRoute,
    private router: Router,
    private productosService: ProductosService
  ) {}

  ngOnInit(): void {
    const id = Number(this.route.snapshot.paramMap.get('id'));

    if (!id) {
      this.error = true;
      return;
    }

    this.cargarProducto(id);
  }

  cargarProducto(id: number): void {
    this.cargando = true;
    this.error = false;

    this.productosService.getPublico(id).subscribe({
      next: (datos) => {
        this.producto = datos;
        this.cargando = false;
      },
      error: () => {
        this.error = true;
        this.cargando = false;
      },
    });
  }

  formatearMoneda(valor: number): string {
    return new Intl.NumberFormat('es-MX', {
      style: 'currency',
      currency: 'MXN',
    }).format(valor);
  }

  descargarManual(idDocumento: number, nombreArchivo: string): void {
    this.descargandoId = idDocumento;
    this.errorDescarga = '';

    this.productosService.descargarDocumento(idDocumento).subscribe({
      next: (documento) => {
        this.descargandoId = null;

        const binario = atob(documento.contenidoBase64);
        const bytes = new Uint8Array(binario.length);
        for (let i = 0; i < binario.length; i++) {
          bytes[i] = binario.charCodeAt(i);
        }

        const blob = new Blob([bytes], { type: documento.tipoContenido });
        const url = URL.createObjectURL(blob);

        const enlace = document.createElement('a');
        enlace.href = url;
        enlace.download = nombreArchivo || documento.nombreArchivo;
        document.body.appendChild(enlace);
        enlace.click();
        document.body.removeChild(enlace);
        URL.revokeObjectURL(url);
      },
      error: () => {
        this.descargandoId = null;
        this.errorDescarga = 'No se pudo descargar la guía o manual.';
      },
    });
  }

  regresar(): void {
    this.router.navigate(['/mis-compras']);
  }
}