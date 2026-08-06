import { Component, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { Router } from '@angular/router';

import { NuevaOrganizacion } from '../../../interfaces/organizacion';
import { OrganizacionesService } from '../../../services/organizaciones';

@Component({
  selector: 'app-nueva-organizacion',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule],
  templateUrl: './organizacion-nuevo.html',
  styleUrl: './organizacion-nuevo.css',
})
export class OrganizacionNuevo {
  private readonly fb = inject(FormBuilder);
  private readonly organizacionesService = inject(OrganizacionesService);
  private readonly router = inject(Router);

  guardando = false;
  errorGuardar: string | null = null;

  readonly form = this.fb.group({
    nombre: ['', [Validators.required, Validators.maxLength(150)]],
    sector: ['', [Validators.required, Validators.maxLength(50)]],
    rol: [{ value: 'organizacion', disabled: true }, [Validators.required]],
    contacto_Principal: ['', [Validators.maxLength(100)]],
    email_Contacto: ['', [Validators.email, Validators.maxLength(100)]],
    contrasena_Hash: ['', [Validators.maxLength(255)]],
    estado_Activo: [true],
    es_Interna: [false],
  });

  /** Getter usado por el template: f['nombre'].touched, f['nombre'].invalid, etc. */
  get f() {
    return this.form.controls;
  }

  guardar(): void {
    this.errorGuardar = null;

    if (this.form.invalid) {
      this.form.markAllAsTouched();
      return;
    }

    this.guardando = true;

    const raw = this.form.getRawValue();

    // Campos opcionales vacíos se envían como null en vez de '' para
    // que el backend los guarde consistentemente como ausentes.
    const payload: NuevaOrganizacion = {
      nombre: raw.nombre!.trim(),
      sector: raw.sector!.trim(),
      rol: raw.rol!,
      contacto_Principal: raw.contacto_Principal?.trim() || null,
      email_Contacto: raw.email_Contacto?.trim() || null,
      contrasena_Hash: raw.contrasena_Hash || null,
      estado_Activo: raw.estado_Activo!,
      es_Interna: raw.es_Interna!,
    };

    this.organizacionesService.create(payload).subscribe({
      next: () => {
        this.guardando = false;
        this.router.navigate(['/organizaciones']);
      },
      error: (err) => {
        this.guardando = false;
        this.errorGuardar =
          err?.error?.error ?? 'No se pudo crear la organización. Verifica los datos e intenta de nuevo.';
      },
    });
  }

  cancelar(): void {
    this.router.navigate(['/organizaciones']);
  }
}
