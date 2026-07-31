import { Component, OnInit } from '@angular/core';
import { RouterLink } from '@angular/router';
import { DispositivosService } from '../../../services/dispositivos';
import { Dispositivo } from '../../../interfaces/dispositivo';
import { Sidebar } from '../../../sidebar/sidebar';
import { DatePipe } from '@angular/common';

@Component({
  selector: 'app-list-dispositivo',
  standalone: true,
  imports: [RouterLink, Sidebar, DatePipe],
  templateUrl: './list-dispositivo.html',
  styleUrl: './list-dispositivo.css',
})
export class ListDispositivo implements OnInit {

  dispositivos: Dispositivo[] = [];
  cargando = true;
  error = false;

  constructor(private dispositivosService: DispositivosService) {}

  ngOnInit(): void {
    this.cargarDispositivos();
  }

  cargarDispositivos(): void {
    this.cargando = true;
    this.error = false;

    this.dispositivosService.getAll().subscribe({
      next: (data) => {
        console.log('DISPOSITIVOS RECIBIDOS:', data);

        this.dispositivos = data;
        this.cargando = false;
      },
      error: (err) => {
        console.error('Error al cargar dispositivos', err);
        this.error = true;
        this.cargando = false;
      },
    });
  }
}