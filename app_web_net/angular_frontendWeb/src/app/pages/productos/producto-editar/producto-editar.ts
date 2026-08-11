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
import { FormsModule } from '@angular/forms';
import { ProductosService } from '../../../services/producto';
import { MateriaPrimaService } from '../../../services/materia-prima';
import {
  MateriaPrima,
  ProductoCreateDto,
  ProductoResumen,
  ContenidoDetalle,
  DocumentoArchivo,
} from '../../../interfaces/producto';

@Component({
  selector: 'app-producto-editar',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule, FormsModule],
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

  // Paquete: extras y guias/manuales
  productos: ProductoResumen[] = [];
  contenido: ContenidoDetalle[] = [];
  documentos: DocumentoArchivo[] = [];

  extraIdItem = '';
  extraCantidad = 1;
  agregandoExtra = false;
  errorExtra = '';

  archivoSeleccionado: File | null = null;
  subiendoDocumento = false;
  errorDocumento = '';
  descripcionDocumento = '';

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
      incluyeMochila: [true],
      receta: this.fb.array([], Validators.required),
    });

    this.cargarMateriasPrimas();
    this.cargarProductos();

    if (!this.registroId) {
      this.error = true;
      this.cargando = false;
      return;
    }

    this.cargarProducto();
  }

  cargarProductos(): void {
    this.productosService.getAll().subscribe({
      next: (datos) => {
        this.productos = datos.filter((p) => p.activo);
      },
      error: () => {},
    });
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
          incluyeMochila: data.incluyeMochila,
        });

        this.contenido = data.contenido ?? [];
        this.documentos = data.documentos ?? [];

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

  // ---- Extras del paquete ----
  productoNombre(idItem: number): string {
    return this.productos.find((p) => p.idProducto === idItem)?.nombre ?? '';
  }

  productosDisponiblesExtras(): ProductoResumen[] {
    const usados = this.contenido.map((c) => c.idItem);
    usados.push(this.registroId);
    return this.productos.filter((p) => !usados.includes(p.idProducto));
  }

  agregarExtra(): void {
    this.errorExtra = '';
    const idItem = Number(this.extraIdItem);
    const cantidad = Number(this.extraCantidad);

    if (!idItem || cantidad < 1) {
      this.errorExtra = 'Selecciona un producto extra y una cantidad válida.';
      return;
    }

    this.agregandoExtra = true;

    this.productosService
      .agregarContenido(this.registroId, { idItem, cantidad })
      .subscribe({
        next: () => {
          this.extraIdItem = '';
          this.extraCantidad = 1;
          this.agregandoExtra = false;
          this.cargarProducto();
        },
        error: (err) => {
          this.agregandoExtra = false;
          this.errorExtra = err?.error?.error || 'No se pudo agregar el extra.';
        },
      });
  }

  quitarExtra(idContenido: number): void {
    this.productosService
      .eliminarContenido(this.registroId, idContenido)
      .subscribe({
        next: () => this.cargarProducto(),
        error: (err) => {
          this.errorExtra = err?.error?.error || 'No se pudo quitar el extra.';
        },
      });
  }

  // ---- Guias y manuales ----
  onArchivoSeleccionado(event: Event): void {
    const input = event.target as HTMLInputElement;
    this.archivoSeleccionado = input.files?.length ? input.files[0] : null;
  }

  subirDocumento(): void {
    this.errorDocumento = '';

    if (!this.archivoSeleccionado) {
      this.errorDocumento = 'Selecciona un archivo primero.';
      return;
    }

    const reader = new FileReader();

    reader.onload = () => {
      const resultado = String(reader.result ?? '').split(',')[1] ?? '';

      this.subiendoDocumento = true;

      this.productosService
        .agregarDocumento(this.registroId, {
          nombreArchivo: this.archivoSeleccionado?.name ?? 'documento',
          tipoContenido: this.archivoSeleccionado?.type || 'application/octet-stream',
          descripcion: this.descripcionDocumento || null,
          contenidoBase64: resultado,
        })
        .subscribe({
          next: () => {
            this.subiendoDocumento = false;
            this.archivoSeleccionado = null;
            this.descripcionDocumento = '';
            this.cargarProducto();
          },
          error: (err) => {
            this.subiendoDocumento = false;
            this.errorDocumento =
              err?.error?.error || 'No se pudo subir la guía o manual.';
          },
        });
    };

    reader.onerror = () => {
      this.errorDocumento = 'No se pudo leer el archivo.';
    };

    reader.readAsDataURL(this.archivoSeleccionado);
  }

  quitarDocumento(idDocumento: number): void {
    this.productosService.eliminarDocumento(idDocumento).subscribe({
      next: () => this.cargarProducto(),
      error: (err) => {
        this.errorDocumento =
          err?.error?.error || 'No se pudo eliminar la guía o manual.';
      },
    });
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
      incluyeMochila: valores.incluyeMochila,
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
