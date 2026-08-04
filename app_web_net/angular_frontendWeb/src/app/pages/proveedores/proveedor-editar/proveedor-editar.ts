import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import {
  FormBuilder,
  FormGroup,
  ReactiveFormsModule,
  Validators,
} from '@angular/forms';
import { ActivatedRoute, Router } from '@angular/router';
import { ProveedoresService } from '../../../services/proveedores';

@Component({
  selector: 'app-proveedor-editar',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule],
  templateUrl: './proveedor-editar.html',
  styleUrl: './proveedor-editar.css',
})
export class ProveedorEditar implements OnInit {

  form!: FormGroup;
  registroId!: number;

  cargando = false;
  guardando = false;
  error = false;
  guardadoExitoso = false;

  constructor(
    private fb: FormBuilder,
    private route: ActivatedRoute,
    private router: Router,
    private proveedoresService: ProveedoresService
  ) {}

  ngOnInit(): void {

    this.registroId = Number(
      this.route.snapshot.paramMap.get('id')
    );

    this.form = this.fb.group({
      nombre: ['', Validators.required],
      telefono: [''],
      correo: ['', [Validators.required, Validators.email]],
      direccion: [''],
      activo: [true],
    });

    this.cargando = true;

    this.proveedoresService.getById(this.registroId)
      .subscribe({
        next: (proveedor) => {

          this.form.patchValue({
            nombre: proveedor.nombre,
            telefono: proveedor.telefono,
            correo: proveedor.correo,
            direccion: proveedor.direccion,
            activo: proveedor.activo
          });

          this.cargando = false;

        },
        error: (err) => {
          console.error(err);
          this.error = true;
          this.cargando = false;
        }
      });

  }

  guardar(): void {

    if (this.form.invalid) {
      this.form.markAllAsTouched();
      return;
    }

    this.guardando = true;

    this.proveedoresService.update(
      this.registroId,
      this.form.value
    )
    .subscribe({
      next: () => {

        this.guardadoExitoso = true;
        this.guardando = false;

        this.router.navigate([
          '/proveedores',
          this.registroId
        ]);

      },
      error: (err) => {

        console.error(err);
        this.guardando = false;

      }
    });

  }

  cancelar(): void {
    this.router.navigate([
      '/proveedores',
      this.registroId
    ]);
  }

  get f() {
    return this.form.controls;
  }

}