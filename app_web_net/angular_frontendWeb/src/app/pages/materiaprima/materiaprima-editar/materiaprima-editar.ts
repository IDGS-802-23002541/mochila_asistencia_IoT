import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { ActivatedRoute, Router } from '@angular/router';
import { MateriaPrimaService } from '../../../services/materia-prima';
import { MateriaPrimaCreateDto } from '../../../interfaces/materiaprima';

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
  eliminando = false;
  error = false;
  errorGuardar = '';
  guardadoExitoso = false;

  constructor(
    private fb: FormBuilder,
    private route: ActivatedRoute,
    private router: Router,
    private materiaPrimaService: MateriaPrimaService
  ) {}

  ngOnInit(): void {
    this.registroId = Number(this.route.snapshot.paramMap.get('id'));

    this.form = this.fb.group({
      nombre: ['', Validators.required],
      descripcion: [''],
      costoUnitario: ['', [Validators.required, Validators.min(0)]],
      stock: [0, [Validators.required, Validators.min(0)]],
      stockMinimo: [0, [Validators.required, Validators.min(0)]],
      idProveedor: ['', [Validators.required, Validators.min(1)]],
    });

    this.cargarRegistro();
  }

  cargarRegistro(): void {
    this.cargando = true;
    this.error = false;

    this.materiaPrimaService.getById(this.registroId).subscribe({
      next: (datos) => {
        this.form.patchValue({
          nombre: datos.nombre,
          descripcion: datos.descripcion,
          costoUnitario: datos.costoUnitario,
          stock: datos.stock,
          stockMinimo: datos.stockMinimo,
          idProveedor: datos.idProveedor,
        });
        this.cargando = false;
      },
      error: () => {
        this.error = true;
        this.cargando = false;
      },
    });
  }

  guardar(): void {
    this.errorGuardar = '';
    this.guardadoExitoso = false;

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

    this.materiaPrimaService.update(this.registroId, dto).subscribe({
      next: () => {
        this.guardando = false;
        this.guardadoExitoso = true;
      },
      error: (err) => {
        this.guardando = false;
        this.errorGuardar =
          err?.error?.error || 'No se pudo guardar la materia prima. Intenta de nuevo.';
      },
    });
  }

  eliminar(): void {
    const confirmado = confirm(
      '¿Seguro que quieres eliminar esta materia prima? Esta acción no se puede deshacer.'
    );
    if (!confirmado) return;

    this.errorGuardar = '';
    this.eliminando = true;

    this.materiaPrimaService.delete(this.registroId).subscribe({
      next: () => {
        this.router.navigate(['/materiaprima']);
      },
      error: (err) => {
        this.eliminando = false;
        this.errorGuardar =
          err?.error?.error ||
          'No se pudo eliminar. Puede que esta materia prima esté siendo usada en la receta de algún producto.';
      },
    });
  }

  cancelar(): void {
    this.router.navigate(['/materiaprima', this.registroId]);
  }

  get f() {
    return this.form.controls;
  }
}
