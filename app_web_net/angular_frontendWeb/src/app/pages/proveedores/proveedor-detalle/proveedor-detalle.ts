import { Component } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { Proveedor } from '../../../interfaces/proveedor';

@Component({
  selector: 'app-proveedor-detalle',
  standalone: true,
  imports: [],
  templateUrl: './proveedor-detalle.html',
  styleUrl: './proveedor-detalle.css',
})
export class ProveedorDetalle {
  // TODO: reemplazar por datos reales del servicio, cargados según route.snapshot.paramMap
  cargando = false;
  error = false;
  eliminando = false;

  registro: Proveedor | null = {
    id: 1,
    nombre: 'Distribuidora Industrial del Bajío',
    estado_Activo: true,
    contacto_Principal: '—',
    telefono: '—',
    email_Contacto: '—',
    direccion: '—',
  };

  constructor(private route: ActivatedRoute, private router: Router) {}

  editar(): void {
    if (!this.registro) return;
    this.router.navigate(['/proveedores', this.registro.id, 'editar']);
  }

  eliminar(): void {
    // TODO: conectar con el servicio para eliminar el registro
  }

  formatearId(id: number): string {
    return id.toString().padStart(4, '0');
  }
}
