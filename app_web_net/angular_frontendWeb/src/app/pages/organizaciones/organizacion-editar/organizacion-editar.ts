import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { ActivatedRoute, Router } from '@angular/router';
import { OrganizacionesService } from '../../../services/organizaciones';
import { Organizacion } from '../../../interfaces/organizacion';
import { Sidebar } from '../../../sidebar/sidebar';

@Component({
  selector: 'app-organizacion-editar',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule, Sidebar],
  templateUrl: './organizacion-editar.html',
  styleUrl: './organizacion-editar.css',
})
export class OrganizacionEditar implements OnInit {
  form!: FormGroup;
  organizacionId!: number;
  organizacionOriginal: Organizacion | null = null;

  cargando = true;
  guardando = false;
  error = false;
  guardadoExitoso = false;

  constructor(
    private fb: FormBuilder,
    private route: ActivatedRoute,
    private router: Router,
    private organizacionesService: OrganizacionesService
  ) {}

  ngOnInit(): void {
    this.organizacionId = Number(this.route.snapshot.paramMap.get('id'));

    this.form = this.fb.group({
      nombre: ['', [Validators.required, Validators.minLength(3)]],
      sector: ['', Validators.required],
      contacto_Principal: ['', Validators.required],
      email_Contacto: ['', [Validators.required, Validators.email]],
      rol: ['', Validators.required],
      estado_Activo: [true],
      es_Interna: [false],
    });

    if (!this.organizacionId) {
      this.error = true;
      this.cargando = false;
      return;
    }

    this.cargarOrganizacion();
  }

  cargarOrganizacion(): void {
    this.cargando = true;
    this.error = false;

    this.organizacionesService.getById(this.organizacionId).subscribe({
      next: (data) => {
        this.organizacionOriginal = data;
        this.form.patchValue({
          nombre: data.nombre,
          sector: data.sector,
          contacto_Principal: data.contacto_Principal,
          email_Contacto: data.email_Contacto,
          rol: data.rol,
          estado_Activo: data.estado_Activo,
          es_Interna: data.es_Interna,
        });
        this.cargando = false;
      },
      error: (err) => {
        console.error('Error al cargar la organización', err);
        this.error = true;
        this.cargando = false;
      },
    });
  }

  guardar(): void {
    if (this.form.invalid) {
      this.form.markAllAsTouched();
      return;
    }
    if (!this.organizacionOriginal) return;

    this.guardando = true;
    this.guardadoExitoso = false;

    const organizacionActualizada: Organizacion = {
      ...this.organizacionOriginal,
      ...this.form.value,
    };

    this.organizacionesService.update(this.organizacionId, organizacionActualizada).subscribe({
      next: () => {
        this.guardando = false;
        this.guardadoExitoso = true;
        setTimeout(() => {
          this.router.navigate(['/clientes', this.organizacionId]);
        }, 800);
      },
      error: (err) => {
        console.error('Error al actualizar la organización', err);
        this.guardando = false;
        alert('No se pudo guardar. Verifica los datos e intenta de nuevo.');
      },
    });
  }

  cancelar(): void {
    this.router.navigate(['/clientes', this.organizacionId]);
  }

  get f() {
    return this.form.controls;
  }
}
