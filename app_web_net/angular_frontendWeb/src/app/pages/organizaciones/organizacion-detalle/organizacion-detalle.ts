import { Component, OnInit } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { OrganizacionesService } from '../../../services/organizaciones';
import { Organizacion } from '../../../interfaces/organizacion';
import { Sidebar } from '../../../sidebar/sidebar';

@Component({
  selector: 'app-organizacion-detalle',
  standalone: true,
  imports: [Sidebar],
  templateUrl: './organizacion-detalle.html',
  styleUrl: './organizacion-detalle.css',
})
export class OrganizacionDetalle implements OnInit {
  organizacion: Organizacion | null = null;
  cargando = true;
  error = false;
  eliminando = false;

  constructor(
    private route: ActivatedRoute,
    private router: Router,
    private organizaciones: OrganizacionesService,
  ) {}

  ngOnInit(): void {
    const id = Number(this.route.snapshot.paramMap.get('id'));
    if (!id) {
      this.error = true;
      this.cargando = false;
      return;
    }
    this.cargarOrganizacion(id);
  }

  cargarOrganizacion(id: number): void {
    this.cargando = true;
    this.error = false;

    this.organizaciones.getById(id).subscribe({
      next: (data) => {
        this.organizacion = data;
        this.cargando = false;
      },
      error: (err) => {
        console.error('Error al cargar la organización', err);
        this.error = true;
        this.cargando = false;
      },
    });
  }

  editar(): void {
    if (!this.organizacion) return;
    this.router.navigate(['/clientes', this.organizacion.id, 'editar']);
  }

  eliminar(): void {
    if (!this.organizacion) return;

    const confirmado = confirm(
      `¿Seguro que quieres eliminar "${this.organizacion.nombre}"? Esta acción no se puede deshacer.`,
    );
    if (!confirmado) return;

    this.eliminando = true;
    this.organizaciones.delete(this.organizacion.id).subscribe({
      next: () => {
        this.router.navigate(['/clientes']);
      },
      error: (err) => {
        console.error('Error al eliminar la organización', err);
        this.eliminando = false;
        alert('No se pudo eliminar la organización. Puede que tenga dependencias asociadas.');
      },
    });
  }

  formatearId(id: number): string {
    return id.toString().padStart(4, '0');
  }
}
