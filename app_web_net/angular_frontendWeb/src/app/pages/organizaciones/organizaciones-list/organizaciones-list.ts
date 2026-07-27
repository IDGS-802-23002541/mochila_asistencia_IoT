import { Component, OnInit } from '@angular/core';
import { RouterLink } from '@angular/router';
import { OrganizacionesService } from '../../../services/organizaciones';
import { Organizacion } from '../../../interfaces/organizacion';
import { Sidebar } from '../../../sidebar/sidebar';

@Component({
  selector: 'app-organizaciones-list',
  standalone: true,
  imports: [RouterLink, Sidebar],
  templateUrl: './organizaciones-list.html',
  styleUrl: './organizaciones-list.css',
})
export class OrganizacionesList implements OnInit {
  organizaciones: Organizacion[] = [];
  cargando = true;
  error = false;

  constructor(private organizacionesService: OrganizacionesService) {}

  ngOnInit(): void {
    this.cargarOrganizaciones();
  }

  cargarOrganizaciones(): void {
    this.cargando = true;
    this.error = false;

    this.organizacionesService.getAll().subscribe({
      next: (data) => {
        this.organizaciones = data;
        this.cargando = false;
      },
      error: (err) => {
        console.error('Error al cargar organizaciones', err);
        this.error = true;
        this.cargando = false;
      },
    });
  }
}
