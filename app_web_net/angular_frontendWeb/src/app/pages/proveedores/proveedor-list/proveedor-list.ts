import { Component, OnInit } from '@angular/core';
import { RouterLink } from '@angular/router';
import { ProveedoresService } from '../../../services/proveedores';
import { Proveedor } from '../../../interfaces/proveedor';

@Component({
  selector: 'app-proveedor-list',
  standalone: true,
  imports: [RouterLink],
  templateUrl: './proveedor-list.html',
  styleUrl: './proveedor-list.css',
})
export class ProveedorList implements OnInit {

  cargando = false;
  error = false;

  proveedores: Proveedor[] = [];

  constructor(
    private proveedoresService: ProveedoresService
  ) {}

  ngOnInit(): void {
    this.cargarProveedores();
  }

  cargarProveedores(): void {

    this.cargando = true;
    this.error = false;

    this.proveedoresService.getAll().subscribe({
      next: (data) => {
        this.proveedores = data;
        this.cargando = false;
      },
      error: (err) => {
        console.error(err);
        this.error = true;
        this.cargando = false;
      }
    });

  }

}