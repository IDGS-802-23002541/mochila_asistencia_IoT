import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { ActivatedRoute, Router } from '@angular/router';

@Component({
  selector: 'app-materiaprima-editar',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule],
  templateUrl: './materiaprima-editar.html',
  styleUrl: './materiaprima-editar.css',
})
export class MateriaPrimaEditar implements OnInit {
  form!: FormGroup;
  registroId!: number;

  cargando = false;
  guardando = false;
  error = false;
  guardadoExitoso = false;

  constructor(
    private fb: FormBuilder,
    private route: ActivatedRoute,
    private router: Router
  ) {}

  ngOnInit(): void {
    this.registroId = Number(this.route.snapshot.paramMap.get('id'));

    this.form = this.fb.group({
      nombre: ['', Validators.required],
      categoria: ['', Validators.required],
      unidad_Medida: ['', Validators.required],
      stock_Actual: [''],
      precio_Unitario: [''],
      proveedor: [''],
      estado_Activo: [true],
    });

    // TODO: cargar el registro real desde el servicio y usar this.form.patchValue(...)
  }

  guardar(): void {
    if (this.form.invalid) {
      this.form.markAllAsTouched();
      return;
    }
    // TODO: conectar con el servicio para actualizar el registro
  }

  cancelar(): void {
    this.router.navigate(['/materiaprima', this.registroId]);
  }

  get f() {
    return this.form.controls;
  }
}
