import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { Router } from '@angular/router';

@Component({
  selector: 'app-producto-nuevo',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule],
  templateUrl: './producto-nuevo.html',
  styleUrl: './producto-nuevo.css',
})
export class ProductoNuevo {
  form: FormGroup;
  guardando = false;

  constructor(private fb: FormBuilder, private router: Router) {
    this.form = this.fb.group({
      nombre: ['', Validators.required],
      categoria: ['', Validators.required],
      precio: ['', Validators.required],
      stock: [''],
      descripcion: [''],
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
    this.router.navigate(['/productos']);
  }

  get f() {
    return this.form.controls;
  }
}
