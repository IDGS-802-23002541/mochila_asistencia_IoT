import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import {
  FormArray,
  FormBuilder,
  FormGroup,
  ReactiveFormsModule,
  Validators,
} from '@angular/forms';
import { ActivatedRoute, Router } from '@angular/router';
import { ProductosService } from '../../../services/producto';
import { MateriaPrimaService } from '../../../services/materia-prima';
import { MateriaPrima, ProductoCreateDto } from '../../../interfaces/producto';

@Component({
  selector: 'app-producto-editar',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule],
  templateUrl: './producto-editar.html',
  styleUrl: './producto-editar.css',
})
export class ProductoEditar implements OnInit {
  form!: FormGroup;
  registroId!: number;

  cargando = false;
  guardando = false;
  error = false;
  guardadoExitoso = false;
  errorGuardar = '';

  materiasPrimas: MateriaPrima[] = [];
  cargandoMaterias = false;

  constructor(
    private fb: FormBuilder,
    private route: ActivatedRoute,
    private router: Router,
    private productosService: ProductosService,
    private materiasPrimasService: MateriaPrimaService
  ) {}

  ngOnInit(): void {
    this.registroId = Number(this.route.snapshot.paramMap.get('id'));

    this.form = this.fb.group({
      nombre: ['', Validators.required],
      precio: ['', [Validators.required, Validators.min(0)]],
      stock: [0, [Validators.min(0)]],
      margenGanancia: [20, [Validators.min(0), Validators.max(100)]],
      descripcion: [''],
      activo: [true],
      receta: this.fb.array([], Validators.required),
    });

    this.cargarMateriasPrimas();

    if (!this.registroId) {
      this.error = true;
      this.cargando = false;
      return;
    }

    this.cargarProducto();
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

  cargarProducto(): void {
    this.cargando = true;
    this.error = false;

    this.productosService.getDetalle(this.registroId).subscribe({
      next: (data) => {
        this.form.patchValue({
          nombre: data.nombre,
          precio: data.precio,
          stock: data.stock,
          margenGanancia: data.margenGanancia,
          descripcion: data.descripcion,
          activo: data.activo,
        });

        this.receta.clear();
        for (const item of data.receta) {
          this.receta.push(
            this.fb.group({
              idMateriaPrima: [item.idMateriaPrima, Validators.required],
              cantidad: [item.cantidad, [Validators.required, Validators.min(1)]],
            })
          );
        }

        this.cargando = false;
      },
      error: () => {
        this.error = true;
        this.cargando = false;
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
    this.guardadoExitoso = false;

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
      activo: valores.activo,
      fotoUrl: null,
      receta: valores.receta.map((r: { idMateriaPrima: string; cantidad: number }) => ({
        idMateriaPrima: Number(r.idMateriaPrima),
        cantidad: Number(r.cantidad),
      })),
    };

    this.guardando = true;

    this.productosService.update(this.registroId, dto).subscribe({
      next: () => {
        this.guardando = false;
        this.guardadoExitoso = true;
        setTimeout(() => {
          this.router.navigate(['/productos/detalle', this.registroId]);
        }, 800);
      },
      error: (err) => {
        this.guardando = false;
        this.errorGuardar =
          err?.error?.error || 'No se pudo guardar el producto. Intenta de nuevo.';
      },
    });
  }

  cancelar(): void {
    if (this.registroId) {
      this.router.navigate(['/productos/detalle', this.registroId]);
      return;
    }
    this.router.navigate(['/productos']);
  }

  get f() {
    return this.form.controls;
  }
}
