import { AfterViewInit, Component, ElementRef, Input, OnDestroy, ViewChild } from '@angular/core';
import { Chart, registerables } from 'chart.js';
import { ZonaAccesibilidad } from '../models/zona-accesibilidad.model';

Chart.register(...registerables);

@Component({
  selector: 'app-grafica-desglose',
  standalone: true,
  imports: [],
  templateUrl: './grafica-desglose.html',
  styleUrl: './grafica-desglose.css',
})
export class GraficaDesglose implements AfterViewInit, OnDestroy {
  @Input({ required: true }) zonas: ZonaAccesibilidad[] = [];
  @ViewChild('canvasDesglose', { static: true }) canvasRef!: ElementRef<HTMLCanvasElement>;

  private chart?: Chart;

  ngAfterViewInit(): void {
    const totalBajo = this.zonas.reduce((acc, z) => acc + z.desglose.bajo, 0);
    const totalMedio = this.zonas.reduce((acc, z) => acc + z.desglose.medio, 0);
    const totalAlto = this.zonas.reduce((acc, z) => acc + z.desglose.alto, 0);

    this.chart = new Chart(this.canvasRef.nativeElement, {
      type: 'doughnut',
      data: {
        labels: ['Bajo', 'Medio', 'Alto'],
        datasets: [{ data: [totalBajo, totalMedio, totalAlto], backgroundColor: ['#16A34A', '#F59E0B', '#DC2626'] }],
      },
      options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { position: 'bottom' } } },
    });
  }

  ngOnDestroy(): void {
    this.chart?.destroy();
  }
}
