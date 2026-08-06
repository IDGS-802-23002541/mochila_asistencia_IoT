import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { Router } from '@angular/router';
import { MateriaPrimaService } from '../../../services/materia-prima';
import { MateriaPrimaCreateDto } from '../../../interfaces/materiaprima';

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
  errorGuardar = '';

  constructor(
    private fb: FormBuilder,
    private router: Router,
    private materiaPrimaService: MateriaPrimaService
  ) {
    this.form = this.fb.group({
      nombre: ['', Validators.required],
      descripcion: [''],
      costoUnitario: ['', [Validators.required, Validators.min(0)]],
      stock: [0, [Validators.required, Validators.min(0)]],
      stockMinimo: [0, [Validators.required, Validators.min(0)]],
      idProveedor: ['', [Validators.required, Validators.min(1)]],
    });
  }

  guardar(): void {
    this.errorGuardar = '';

    if (this.form.invalid) {
      this.form.markAllAsTouched();
      return;
    }

    const valores = this.form.value;

    const dto: MateriaPrimaCreateDto = {
      nombre: valores.nombre,
      descripcion: valores.descripcion || null,
      costoUnitario: Number(valores.costoUnitario),
      stock: Number(valores.stock) || 0,
      stockMinimo: Number(valores.stockMinimo) || 0,
      idProveedor: Number(valores.idProveedor),
    };

    this.guardando = true;

    this.materiaPrimaService.create(dto).subscribe({
      next: (creado) => {
        this.guardando = false;
        this.router.navigate(['/materiaprima', creado.idMateriaPrima]);
      },
      error: (err) => {
        this.guardando = false;
        this.errorGuardar =
          err?.error?.error || 'No se pudo guardar la materia prima. Intenta de nuevo.';
      },
    });
  }

  cancelar(): void {
    this.router.navigate(['/materiaprima']);
  }

  get f() {
    return this.form.controls;
  }
}
