import { Component, OnInit, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ActivatedRoute, Router } from '@angular/router';
import { ProductosService } from '../../../services/producto';
import { ComentariosService } from '../../../services/comentarios';
import { SesionService } from '../../../services/sesion';
import { ProductoPublico } from '../../../interfaces/producto';
import { CrearComentarioDto } from '../../../interfaces/comentario';

@Component({
  selector: 'app-productos',
  imports: [CommonModule, FormsModule],
  templateUrl: './productos.html',
  styleUrl: './productos.css',
})
export class MisProductos implements OnInit {
  cargando = false;
  error = false;
  producto: ProductoPublico | null = null;
  descargandoId: number | null = null;
  errorDescarga = '';

  // Variables para el modal de opinión
  mostrarModalOpinion: boolean = false;
  nombreCliente: string = '';
  correoCliente: string = '';
  opinionTexto: string = '';
  enviandoOpinion: boolean = false;
  errorModal: string = '';

  private comentariosService = inject(ComentariosService);
  private sesionService = inject(SesionService);

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

  // Métodos para el modal de opinión
  abrirModalOpinion(): void {
    const usuario = this.sesionService.obtenerUsuario();
    if (usuario) {
      this.nombreCliente = usuario.nombre || usuario.nombreCliente || '';
      this.correoCliente = usuario.correo || usuario.correoCliente || '';
    }
    this.opinionTexto = '';
    this.errorModal = '';
    this.mostrarModalOpinion = true;
  }

  cerrarModalOpinion(): void {
    this.mostrarModalOpinion = false;
  }

  enviarOpinion(): void {
  if (!this.nombreCliente.trim() || !this.correoCliente.trim() || !this.opinionTexto.trim()) {
    this.errorModal = 'Por favor completa todos los campos.';
    return;
  }

  if (!this.producto) return;

  this.enviandoOpinion = true;
  this.errorModal = '';

  const dto: CrearComentarioDto = {
    nombreCliente: this.nombreCliente.trim(),
    correoCliente: this.correoCliente.trim(),
    mensaje: `[Opinión - Paquete: ${this.producto.nombre}] ${this.opinionTexto.trim()}`
  };

  this.comentariosService.crear(dto).subscribe({
    next: () => {
      this.enviandoOpinion = false;
      this.cerrarModalOpinion();
      alert('¡Gracias por tu opinión! Se ha publicado con éxito.');
    },
    error: (err) => {
      console.error('Error al enviar opinión:', err);

      if (err.status === 0) {
        this.errorModal = 'No se pudo conectar con el servidor. Verifica que el Backend esté corriendo en http://localhost:5103.';
      } else {
        this.errorModal = `Error (${err.status}): ${err.error?.mensaje || 'Error al procesar la solicitud.'}`;
      }

      this.enviandoOpinion = false;
    }
  });
}
}
