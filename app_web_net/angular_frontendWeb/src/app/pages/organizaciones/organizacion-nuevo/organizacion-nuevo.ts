import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { Router } from '@angular/router';
import { OrganizacionesService } from '../../../services/organizaciones';
import { Sidebar } from '../../../sidebar/sidebar';

@Component({
  selector: 'app-organizacion-nuevo',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule, Sidebar],
  templateUrl: './organizacion-nuevo.html',
  styleUrl: './organizacion-nuevo.css',
})
export class OrganizacionNuevo {
  form: FormGroup;
  guardando = false;

  constructor(
    private fb: FormBuilder,
    private router: Router,
    private organizacionesService: OrganizacionesService
  ) {
    this.form = this.fb.group({
      nombre: ['', [Validators.required, Validators.maxLength(150)]],
      sector: ['', Validators.required],
      contacto_Principal: [''],
      email_Contacto: ['', Validators.email],
      rol: ['usuario', Validators.required],
      contrasena_Hash: [''],
      estado_Activo: [true],
      es_Interna: [false],
    });
  }

  guardar(): void {
    if (this.form.invalid) {
      this.form.markAllAsTouched();
      return;
    }

    this.guardando = true;

    this.organizacionesService.create(this.form.value).subscribe({
      next: (nueva) => {
        this.guardando = false;
        this.router.navigate(['/clientes', nueva.id]);
      },
      error: (err) => {
        console.error('Error al crear la organización', err);
        this.guardando = false;
        alert('No se pudo crear la organización. Verifica los datos e intenta de nuevo.');
      },
    });
  }

  cancelar(): void {
    this.router.navigate(['/organizaciones']);
  }

  get f() {
    return this.form.controls;
  }
}
