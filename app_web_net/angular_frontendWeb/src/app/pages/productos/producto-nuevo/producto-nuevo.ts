import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import {
  FormArray,
  FormBuilder,
  FormGroup,
  ReactiveFormsModule,
  Validators,
} from '@angular/forms';
import { Router } from '@angular/router';
import { ProductosService } from '../../../services/producto';
import { MateriaPrimaService } from '../../../services/materia-prima';
import { MateriaPrima, ProductoCreateDto } from '../../../interfaces/producto';

@Component({
  selector: 'app-producto-nuevo',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule],
  templateUrl: './producto-nuevo.html',
  styleUrl: './producto-nuevo.css',
})
export class ProductoNuevo implements OnInit {
  form: FormGroup;
  guardando = false;
  errorGuardar = '';

  materiasPrimas: MateriaPrima[] = [];
  cargandoMaterias = false;

  constructor(
    private fb: FormBuilder,
    private router: Router,
    private productosService: ProductosService,
    private materiasPrimasService: MateriaPrimaService
  ) {
    this.form = this.fb.group({
      nombre: ['', Validators.required],
      precio: ['', [Validators.required, Validators.min(0)]],
      stock: [0, [Validators.min(0)]],
      margenGanancia: [20, [Validators.min(0), Validators.max(100)]],
      descripcion: [''],
      estado_Activo: [true],
      receta: this.fb.array([], Validators.required),
    });
  }

  ngOnInit(): void {
    this.cargarMateriasPrimas();
    this.agregarItemReceta();
  }

  cargarMateriasPrimas(): void {
    this.cargandoMaterias = true;
    this.materiasPrimasService.getAll().subscribe({
      next: (datos) => {
        this.materiasPrimas = datos;
        this.cargandoMaterias = false;
      },
      error: () => {
        this.cargandoMaterias = false;
      },
    });
  }

  get receta(): FormArray {
    return this.form.get('receta') as FormArray;
  }

  idsSeleccionados(indiceActual: number): number[] {
    return this.receta.controls
      .map((c, i) => (i === indiceActual ? null : Number(c.get('idMateriaPrima')?.value)))
      .filter((v): v is number => !!v);
  }

  materiasDisponiblesPara(indice: number): MateriaPrima[] {
    const usados = this.idsSeleccionados(indice);
    return this.materiasPrimas.filter((m) => !usados.includes(m.idMateriaPrima));
  }

  agregarItemReceta(): void {
    this.receta.push(
      this.fb.group({
        idMateriaPrima: ['', Validators.required],
        cantidad: [1, [Validators.required, Validators.min(1)]],
      })
    );
  }

  quitarItemReceta(index: number): void {
    if (this.receta.length === 1) {
      // Siempre debe quedar al menos un renglón para poder capturar la receta.
      this.receta.at(0).reset({ idMateriaPrima: '', cantidad: 1 });
      return;
    }
    this.receta.removeAt(index);
  }

  nombreMateria(idMateriaPrima: number): string {
    return this.materiasPrimas.find((m) => m.idMateriaPrima === +idMateriaPrima)?.nombre ?? '';
  }

  guardar(): void {
    this.errorGuardar = '';

    if (this.form.invalid || this.receta.length === 0) {
      this.form.markAllAsTouched();
      return;
    }

    const valores = this.form.value;

    const dto: ProductoCreateDto = {
      nombre: valores.nombre,
      descripcion: valores.descripcion || null,
      precio: Number(valores.precio),
      stock: Number(valores.stock) || 0,
      margenGanancia: Number(valores.margenGanancia) || 0,
      activo: valores.estado_Activo,
      fotoUrl: null,
      receta: valores.receta.map((r: { idMateriaPrima: string; cantidad: number }) => ({
        idMateriaPrima: Number(r.idMateriaPrima),
        cantidad: Number(r.cantidad),
      })),
    };

    this.guardando = true;

    this.productosService.create(dto).subscribe({
      next: (res) => {
        this.guardando = false;
        this.router.navigate(['/productos', res.idProducto]);
      },
      error: (err) => {
        this.guardando = false;
        this.errorGuardar =
          err?.error?.error || 'No se pudo guardar el producto. Intenta de nuevo.';
      },
    });
  }

  cancelar(): void {
    this.router.navigate(['/productos']);
  }

  get f() {
    return this.form.controls;
  }
}
