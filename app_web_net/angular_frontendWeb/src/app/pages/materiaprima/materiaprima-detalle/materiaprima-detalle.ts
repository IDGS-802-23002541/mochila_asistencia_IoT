import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, Router, RouterLink } from '@angular/router';
import { MateriaPrima } from '../../../interfaces/materiaprima';
import { MateriaPrimaService } from '../../../services/materia-prima';

@Component({
  selector: 'app-materiaprima-detalle',
  standalone: true,
  imports: [CommonModule, RouterLink],
  templateUrl: './materiaprima-detalle.html',
  styleUrl: './materiaprima-detalle.css',
})
export class MateriaPrimaDetalle implements OnInit {
  cargando = false;
  error = false;
  eliminando = false;

  registro: MateriaPrima | null = null;

  constructor(
    private route: ActivatedRoute,
    private router: Router,
    private materiaPrimaService: MateriaPrimaService
  ) {}

  ngOnInit(): void {
    const id = Number(this.route.snapshot.paramMap.get('id'));
    this.cargarRegistro(id);
  }

  cargarRegistro(id: number): void {
    this.cargando = true;
    this.error = false;

    this.materiaPrimaService.getById(id).subscribe({
      next: (datos) => {
        this.registro = datos;
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
    this.router.navigate(['/materiaprima', this.registro.idMateriaPrima, 'editar']);
  }

  eliminar(): void {
    if (!this.registro) return;

    const confirmado = confirm(
      '¿Seguro que quieres eliminar esta materia prima? Esta acción no se puede deshacer.'
    );
    if (!confirmado) return;

    this.eliminando = true;
    this.materiaPrimaService.delete(this.registro.idMateriaPrima).subscribe({
      next: () => {
        this.router.navigate(['/materiaprima']);
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
