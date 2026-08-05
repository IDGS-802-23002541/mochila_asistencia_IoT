import { Component, OnInit, computed, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import {
  AbstractControl,
  FormBuilder,
  ReactiveFormsModule,
  ValidationErrors,
  Validators,
} from '@angular/forms';

import { Organizacion } from '../../interfaces/organizacion';
import { OrganizacionesService } from '../../services/organizaciones';

function passwordsMatchValidator(group: AbstractControl): ValidationErrors | null {
  const nueva = group.get('nuevaContrasena')?.value as string;
  const confirmar = group.get('confirmarContrasena')?.value as string;
  if (!nueva && !confirmar) return null;
  return nueva === confirmar ? null : { passwordMismatch: true };
}
@Component({
  selector: 'app-ajustes-organizacion',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule],
  templateUrl: './ajustes.html',
  styleUrl: './ajustes.css',
})
export class Ajustes implements OnInit {
  private readonly fb = inject(FormBuilder);
  private readonly organizacionesService = inject(OrganizacionesService);

  readonly loading = signal(true);
  readonly saving = signal(false);
  readonly loadError = signal<string | null>(null);
  readonly saveError = signal<string | null>(null);
  readonly saveSuccess = signal(false);

  readonly organizacion = signal<Organizacion | null>(null);
  readonly avatarPreview = signal<string | null>(null);
  readonly changingPassword = signal(false);

  readonly initials = computed(() => {
    const nombre = this.organizacion()?.nombre ?? '';
    return nombre
      .trim()
      .split(/\s+/)
      .slice(0, 2)
      .map((p) => p.charAt(0).toUpperCase())
      .join('');
  });

  readonly form = this.fb.nonNullable.group({
    nombre: ['', [Validators.required, Validators.maxLength(150)]],
    sector: ['', [Validators.required, Validators.maxLength(50)]],
    contacto_Principal: ['', [Validators.maxLength(100)]],
    email_Contacto: ['', [Validators.email, Validators.maxLength(100)]],
    fotoUrl: [''],
    seguridad: this.fb.nonNullable.group(
      {
        nuevaContrasena: [''],
        confirmarContrasena: [''],
      },
      { validators: passwordsMatchValidator }
    ),
  });

  organizacionId = 1;

  ngOnInit(): void {
    this.cargarOrganizacion();
  }

  cargarOrganizacion(): void {
    this.loading.set(true);
    this.loadError.set(null);

    this.organizacionesService.getById(this.organizacionId).subscribe({
      next: (org) => {
        this.organizacion.set(org);
        this.form.patchValue({
          nombre: org.nombre,
          sector: org.sector,
          contacto_Principal: org.contacto_Principal ?? '',
          email_Contacto: org.email_Contacto ?? '',
          fotoUrl: org.fotoUrl ?? '',
        });
        this.avatarPreview.set(org.fotoUrl ?? null);
        this.loading.set(false);
      },
      error: () => {
        this.loadError.set('No se pudo cargar la información de la organización. Intenta de nuevo.');
        this.loading.set(false);
      },
    });
  }

  onFotoSeleccionada(event: Event): void {
    const input = event.target as HTMLInputElement;
    const file = input.files?.[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = () => {
      const dataUrl = reader.result as string;
      this.avatarPreview.set(dataUrl);
      this.form.patchValue({ fotoUrl: dataUrl });
    };
    reader.readAsDataURL(file);
  }

  toggleCambiarContrasena(): void {
    this.changingPassword.update((v) => !v);
    if (!this.changingPassword()) {
      this.form.controls.seguridad.reset({ nuevaContrasena: '', confirmarContrasena: '' });
    }
  }

  guardar(): void {
    this.saveSuccess.set(false);
    this.saveError.set(null);

    if (this.form.invalid) {
      this.form.markAllAsTouched();
      return;
    }

    const actual = this.organizacion();
    if (!actual) return;

    this.saving.set(true);

    const { nombre, sector, contacto_Principal, email_Contacto, fotoUrl, seguridad } =
      this.form.getRawValue();

    const contrasenaHash =
      this.changingPassword() && seguridad.nuevaContrasena ? seguridad.nuevaContrasena : '';

    const payload: Organizacion = {
      ...actual,
      nombre: nombre.trim(),
      sector: sector.trim(),
      contacto_Principal: contacto_Principal?.trim() || null,
      email_Contacto: email_Contacto?.trim() || null,
      fotoUrl: fotoUrl || null,
      contrasena_Hash: contrasenaHash,
    };

    this.organizacionesService.update(actual.id, payload).subscribe({
      next: (updated) => {
        this.organizacion.set(updated);
        this.saving.set(false);
        this.saveSuccess.set(true);
        this.changingPassword.set(false);
        this.form.controls.seguridad.reset({ nuevaContrasena: '', confirmarContrasena: '' });
      },
      error: (err) => {
        this.saving.set(false);
        this.saveError.set(
          err?.error?.error ?? 'No se pudieron guardar los cambios. Verifica los datos e intenta de nuevo.'
        );
      },
    });
  }

  cancelar(): void {
    const org = this.organizacion();
    if (!org) return;
    this.form.patchValue({
      nombre: org.nombre,
      sector: org.sector,
      contacto_Principal: org.contacto_Principal ?? '',
      email_Contacto: org.email_Contacto ?? '',
      fotoUrl: org.fotoUrl ?? '',
    });
    this.avatarPreview.set(org.fotoUrl ?? null);
    this.changingPassword.set(false);
    this.form.controls.seguridad.reset({ nuevaContrasena: '', confirmarContrasena: '' });
    this.saveError.set(null);
    this.saveSuccess.set(false);
  }
}
