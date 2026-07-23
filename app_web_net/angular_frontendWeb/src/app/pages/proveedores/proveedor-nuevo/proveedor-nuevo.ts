import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { Router } from '@angular/router';

@Component({
  selector: 'app-proveedor-nuevo',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule],
  templateUrl: './proveedor-nuevo.html',
  styleUrl: './proveedor-nuevo.css',
})
export class ProveedorNuevo {
  form: FormGroup;
  guardando = false;

  constructor(private fb: FormBuilder, private router: Router) {
    this.form = this.fb.group({
      nombre: ['', Validators.required],
      contacto_Principal: ['', Validators.required],
      telefono: [''],
      email_Contacto: ['', [Validators.required, Validators.email]],
      direccion: [''],
      estado_Activo: [true],
    });
  }

  guardar(): void {
    if (this.form.invalid) {
      this.form.markAllAsTouched();
      return;
    }
    // TODO: conectar con el servicio para crear el registro
  }

  cancelar(): void {
    this.router.navigate(['/proveedores']);
  }

  get f() {
    return this.form.controls;
  }
}
