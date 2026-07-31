import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { Router } from '@angular/router';

@Component({
  selector: 'app-materiaprima-nuevo',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule],
  templateUrl: './materiaprima-nuevo.html',
  styleUrl: './materiaprima-nuevo.css',
})
export class MateriaPrimaNuevo {
  form: FormGroup;
  guardando = false;

  constructor(private fb: FormBuilder, private router: Router) {
    this.form = this.fb.group({
      nombre: ['', Validators.required],
      categoria: ['', Validators.required],
      unidad_Medida: ['', Validators.required],
      stock_Actual: [''],
      precio_Unitario: [''],
      proveedor: [''],
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
    this.router.navigate(['/materiaprima']);
  }

  get f() {
    return this.form.controls;
  }
}
