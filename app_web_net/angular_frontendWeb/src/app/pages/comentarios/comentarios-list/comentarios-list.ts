import { Component, OnInit, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ComentariosService } from '../../../services/comentarios';
import { Comentario, ActualizarComentarioDto } from '../../../interfaces/comentario';

@Component({
  selector: 'app-comentarios-list',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './comentarios-list.html',
  styleUrls: ['./comentarios-list.css']
})
export class ComentariosListComponent implements OnInit {
  private comentariosService = inject(ComentariosService);

  comentarios: Comentario[] = [];
  filtroEstado: string = '';
  comentarioSeleccionado: Comentario | null = null;

  // Campos del modal
  nuevoEstado: 'Pendiente' | 'EnRevision' | 'Atendido' = 'EnRevision';
  respuestaTexto: string = '';
  cargando: boolean = false;
  error: string = '';

  ngOnInit(): void {
    this.cargarComentarios();
  }

  cargarComentarios(): void {
    this.cargando = true;
    this.error = '';
    this.comentariosService.obtenerTodos(this.filtroEstado).subscribe({
      next: (data) => {
        this.comentarios = data;
        this.cargando = false;
      },
      error: (err) => {
        console.error('Error al cargar comentarios:', err);
        this.error = 'No se pudieron cargar los comentarios.';
        this.cargando = false;
      }
    });
  }

  filtrarPor(estado: string): void {
    this.filtroEstado = estado;
    this.cargarComentarios();
  }

  abrirDetalle(comentario: Comentario): void {
    this.comentarioSeleccionado = { ...comentario };
    this.nuevoEstado = comentario.estado;
    this.respuestaTexto = comentario.respuestaAdministrador || '';
  }

  cerrarDetalle(): void {
    this.comentarioSeleccionado = null;
  }

  guardarSeguimiento(): void {
    if (!this.comentarioSeleccionado) return;

    const dto: ActualizarComentarioDto = {
      estado: this.nuevoEstado,
      respuestaAdministrador: this.respuestaTexto
    };

    this.comentariosService.actualizar(this.comentarioSeleccionado.idComentario, dto).subscribe({
      next: () => {
        this.cerrarDetalle();
        this.cargarComentarios();
      },
      error: (err) => console.error('Error guardando seguimiento:', err)
    });
  }

  obtenerInicial(nombre?: string): string {
    return nombre && nombre.length > 0 ? nombre.charAt(0).toUpperCase() : 'C';
  }
}
