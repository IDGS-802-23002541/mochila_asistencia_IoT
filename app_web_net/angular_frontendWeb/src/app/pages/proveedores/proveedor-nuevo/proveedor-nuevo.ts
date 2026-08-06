import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { Router } from '@angular/router';
import { ProveedoresService } from '../../../services/proveedores';
import { Proveedor } from '../../../interfaces/proveedor';

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

  constructor(
    private fb: FormBuilder,
    private router: Router,
    private proveedoresService: ProveedoresService
  ) {

    this.form = this.fb.group({

      nombre: [
        '',
        Validators.required
      ],

      telefono: [
        ''
      ],

      correo: [
        '',
        [
          Validators.required,
          Validators.email
        ]
      ],

      direccion: [
        ''
      ],

      activo: [
        true
      ]

    });

  }


  guardar(): void {

    if (this.form.invalid) {
      this.form.markAllAsTouched();
      return;
    }


    this.guardando = true;


    this.proveedoresService.create(
      this.form.value
    )
    .subscribe({

      next: (nuevoProveedor) => {

        this.guardando = false;


        // Si la API devuelve el id generado
        if (nuevoProveedor.idProveedor) {

          this.router.navigate([
            '/proveedores',
            nuevoProveedor.idProveedor
          ]);

        } else {

          this.router.navigate([
            '/proveedores'
          ]);

        }

      },


      error: (error) => {

        console.error(
          'Error al crear proveedor:',
          error
        );

        this.guardando = false;

      }

    });

  }


  cancelar(): void {

    this.router.navigate([
      '/proveedores'
    ]);

  }


  get f() {

    return this.form.controls;

  }

}