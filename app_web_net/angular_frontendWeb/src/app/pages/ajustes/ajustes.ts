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
import { Usuario } from '../../interfaces/usuario';
import { OrganizacionesService } from '../../services/organizaciones';
import { UsuariosService } from '../../services/usuarios';
import { SesionService } from '../../services/sesion';

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
  private readonly usuariosService = inject(UsuariosService);
  private readonly sesionService = inject(SesionService);

  readonly loading = signal(true);
  readonly saving = signal(false);
  readonly loadError = signal<string | null>(null);
  readonly saveError = signal<string | null>(null);
  readonly saveSuccess = signal(false);

  readonly esOrganizacion = this.sesionService.esOrganizacion;

  readonly organizacion = signal<Organizacion | null>(null);
  readonly usuario = signal<Usuario | null>(null);

  readonly avatarPreview = signal<string | null>(null);
  readonly changingPassword = signal(false);

  readonly initials = computed(() => {
    const nombre = this.esOrganizacion()
      ? (this.organizacion()?.nombre ?? '')
      : (this.usuario()?.nombre ?? '');
    return nombre
      .trim()
      .split(/\s+/)
      .slice(0, 2)
      .map((p) => p.charAt(0).toUpperCase())
      .join('');
  });

  readonly orgForm = this.fb.nonNullable.group({
    nombre: ['', [Validators.required, Validators.maxLength(150)]],
    sector: ['', [Validators.required, Validators.maxLength(50)]],
    contacto_Principal: ['', [Validators.maxLength(100)]],
    email_Contacto: ['', [Validators.email, Validators.maxLength(100)]],
    fotoUrl: [''],
    seguridad: this.fb.nonNullable.group(
      { nuevaContrasena: [''], confirmarContrasena: [''] },
      { validators: passwordsMatchValidator }
    ),
  });

  readonly userForm = this.fb.nonNullable.group({
    nombre: ['', [Validators.required, Validators.maxLength(150)]],
    correo: ['', [Validators.required, Validators.email, Validators.maxLength(150)]],
    fotoUrl: [''],
    seguridad: this.fb.nonNullable.group(
      { nuevaContrasena: [''], confirmarContrasena: [''] },
      { validators: passwordsMatchValidator }
    ),
  });

  get form() {
    return this.esOrganizacion() ? this.orgForm : this.userForm;
  }

  ngOnInit(): void {
    const sesion = this.sesionService.sesion();
    if (!sesion) {
      this.loadError.set('No hay una sesión activa.');
      this.loading.set(false);
      return;
    }

    if (this.esOrganizacion()) {
      this.cargarOrganizacion(sesion.organizacionId);
    } else {
      this.cargarUsuario(sesion.id);
    }
  }

  cargarOrganizacion(organizacionId: number): void {
    this.loading.set(true);
    this.loadError.set(null);

    this.organizacionesService.getById(organizacionId).subscribe({
      next: (org) => {
        this.organizacion.set(org);
        this.orgForm.patchValue({
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

  cargarUsuario(usuarioId: number): void {
    this.loading.set(true);
    this.loadError.set(null);

    this.usuariosService.getById(usuarioId).subscribe({
      next: (u) => {
        this.usuario.set(u);
        this.userForm.patchValue({
          nombre: u.nombre,
          correo: u.correo,
          fotoUrl: u.fotoUrl ?? '',
        });
        this.avatarPreview.set(u.fotoUrl ?? null);
        this.loading.set(false);
      },
      error: () => {
        this.loadError.set('No se pudo cargar tu información. Intenta de nuevo.');
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
      this.form.patchValue({ fotoUrl: dataUrl } as any);
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

    this.saving.set(true);
    this.esOrganizacion() ? this.guardarOrganizacion() : this.guardarUsuario();
  }

  private guardarOrganizacion(): void {
    const actual = this.organizacion();
    if (!actual) {
      this.saving.set(false);
      return;
    }

    const { nombre, sector, contacto_Principal, email_Contacto, fotoUrl, seguridad } =
      this.orgForm.getRawValue();

    const nuevaContrasena =
      this.changingPassword() && seguridad.nuevaContrasena ? seguridad.nuevaContrasena : '';

    const payload: Organizacion = {
      ...actual,
      nombre: nombre.trim(),
      sector: sector.trim(),
      contacto_Principal: contacto_Principal?.trim() || null,
      email_Contacto: email_Contacto?.trim() || null,
      fotoUrl: fotoUrl || null,
      contrasena_Hash: nuevaContrasena, // vacío = el backend no la toca
    };

    this.organizacionesService.update(actual.id, payload).subscribe({
      next: (updated) => {
        this.organizacion.set(updated);
        this.finalizarGuardado();
      },
      error: (err) => this.manejarErrorGuardado(err),
    });
  }

  private guardarUsuario(): void {
    const actual = this.usuario();
    if (!actual) {
      this.saving.set(false);
      return;
    }

    const { nombre, correo, fotoUrl, seguridad } = this.userForm.getRawValue();

    const nuevaContrasena =
      this.changingPassword() && seguridad.nuevaContrasena ? seguridad.nuevaContrasena : '';

    const payload: Usuario = {
      ...actual,
      nombre: nombre.trim(),
      correo: correo.trim(),
      fotoUrl: fotoUrl || null,
      contrasena_Hash: nuevaContrasena,
    };

    this.usuariosService.update(actual.id, payload).subscribe({
      next: (updated) => {
        this.usuario.set(updated);
        this.finalizarGuardado();
      },
      error: (err) => this.manejarErrorGuardado(err),
    });
  }

  private finalizarGuardado(): void {
    this.saving.set(false);
    this.saveSuccess.set(true);
    this.changingPassword.set(false);
    this.form.controls.seguridad.reset({ nuevaContrasena: '', confirmarContrasena: '' });
  }

  private manejarErrorGuardado(err: any): void {
    this.saving.set(false);
    this.saveError.set(
      err?.error?.error ?? 'No se pudieron guardar los cambios. Verifica los datos e intenta de nuevo.'
    );
  }

  cancelar(): void {
    if (this.esOrganizacion()) {
      const org = this.organizacion();
      if (!org) return;
      this.orgForm.patchValue({
        nombre: org.nombre,
        sector: org.sector,
        contacto_Principal: org.contacto_Principal ?? '',
        email_Contacto: org.email_Contacto ?? '',
        fotoUrl: org.fotoUrl ?? '',
      });
      this.avatarPreview.set(org.fotoUrl ?? null);
    } else {
      const u = this.usuario();
      if (!u) return;
      this.userForm.patchValue({
        nombre: u.nombre,
        correo: u.correo,
        fotoUrl: u.fotoUrl ?? '',
      });
      this.avatarPreview.set(u.fotoUrl ?? null);
    }
    this.changingPassword.set(false);
    this.form.controls.seguridad.reset({ nuevaContrasena: '', confirmarContrasena: '' });
    this.saveError.set(null);
    this.saveSuccess.set(false);
  }
}
