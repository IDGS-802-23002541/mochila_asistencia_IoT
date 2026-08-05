import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';
import { MateriaPrima } from '../../../interfaces/materiaprima';
import { MateriaPrimaService } from '../../../services/materia-prima';

@Component({
  selector: 'app-materiaprima-list',
  standalone: true,
  imports: [CommonModule, RouterLink],
  templateUrl: './materiaprima-list.html',
  styleUrl: './materiaprima-list.css',
})
export class MateriaPrimaList implements OnInit {
  cargando = false;
  error = false;

  materiaprima: MateriaPrima[] = [];

  constructor(private materiaPrimaService: MateriaPrimaService) {}

  ngOnInit(): void {
    this.cargarMateriaPrima();
  }

  cargarMateriaPrima(): void {
    this.cargando = true;
    this.error = false;

    this.materiaPrimaService.getAll().subscribe({
      next: (datos) => {
        this.materiaprima = datos;
        this.cargando = false;
      },
      error: () => {
        this.error = true;
        this.cargando = false;
      },
    });
  }

  stockBajo(item: MateriaPrima): boolean {
    return item.stock <= item.stockMinimo;
  }
}
