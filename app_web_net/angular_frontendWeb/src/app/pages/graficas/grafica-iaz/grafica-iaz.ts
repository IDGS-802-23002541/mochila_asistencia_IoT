import { AfterViewInit, Component, ElementRef, Input, OnDestroy, ViewChild } from '@angular/core';
import { Chart, registerables } from 'chart.js';
import { ZonaAccesibilidad } from '../models/zona-accesibilidad.model';

Chart.register(...registerables);

@Component({
  selector: 'app-grafica-iaz',
  standalone: true,
  imports: [],
  templateUrl: './grafica-iaz.html',
  styleUrl: './grafica-iaz.css',
})
export class GraficaIaz implements AfterViewInit, OnDestroy {
  @Input({ required: true }) zonas: ZonaAccesibilidad[] = [];
  @ViewChild('canvasIaz', { static: true }) canvasRef!: ElementRef<HTMLCanvasElement>;

  private chart?: Chart;

  ngAfterViewInit(): void {
    const zonasOrdenadas = [...this.zonas].sort((a, b) => b.iaz - a.iaz);

    this.chart = new Chart(this.canvasRef.nativeElement, {
      type: 'bar',
      data: {
        labels: zonasOrdenadas.map(z => z.zonaId),
        datasets: [{
          label: 'Índice de Accesibilidad por Zona (IAZ)',
          data: zonasOrdenadas.map(z => z.iaz),
          backgroundColor: zonasOrdenadas.map(z =>
            z.iaz >= 5 ? '#DC2626' : z.iaz >= 3 ? '#F59E0B' : '#16A34A'
          ),
          borderRadius: 6,
        }],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { display: false } },
        scales: { y: { beginAtZero: true, title: { display: true, text: 'IAZ' } } },
      },
    });
  }

  ngOnDestroy(): void {
    this.chart?.destroy();
  }
}
