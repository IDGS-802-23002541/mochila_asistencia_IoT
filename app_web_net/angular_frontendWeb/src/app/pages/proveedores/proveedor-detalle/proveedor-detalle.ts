import { Component, OnInit } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { Proveedor } from '../../../interfaces/proveedor';
import { ProveedoresService } from '../../../services/proveedores';

@Component({
  selector: 'app-proveedor-detalle',
  standalone: true,
  imports: [],
  templateUrl: './proveedor-detalle.html',
  styleUrl: './proveedor-detalle.css',
})
export class ProveedorDetalle implements OnInit {

  cargando = false;
  error = false;
  eliminando = false;

  registro: Proveedor | null = null;

  constructor(
    private route: ActivatedRoute,
    private router: Router,
    private proveedoresService: ProveedoresService
  ) {}

  ngOnInit(): void {

    const id = Number(this.route.snapshot.paramMap.get('id'));

    if (!id) {
      this.error = true;
      return;
    }

    this.cargando = true;

    this.proveedoresService.getById(id).subscribe({
      next: (proveedor) => {
        this.registro = proveedor;
        this.cargando = false;
      },
      error: (err) => {
        console.error(err);
        this.error = true;
        this.cargando = false;
      }
    });

  }

  editar(): void {

    if (!this.registro) return;

    this.router.navigate([
      '/proveedores',
      this.registro.idProveedor,
      'editar'
    ]);

  }

  eliminar(): void {

    if (!this.registro) return;

    this.eliminando = true;

    this.proveedoresService
      .delete(this.registro.idProveedor)
      .subscribe({
        next: () => {
          this.router.navigate(['/proveedores']);
        },
        error: (err) => {
          console.error(err);
          this.eliminando = false;
        }
      });

  }

  formatearId(id: number): string {
    return id.toString().padStart(4, '0');
  }

}