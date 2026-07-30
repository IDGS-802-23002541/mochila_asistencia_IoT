import { AfterViewInit, Component, ElementRef, Input, OnDestroy, ViewChild } from '@angular/core';
import { Chart, registerables } from 'chart.js';
import { ZonaAccesibilidad, DesgloseSeveridad } from '../models/zona-accesibilidad.model';

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
    const totalBaja = this.zonas.reduce((acc, z) => acc + z.desgloseSeveridad.baja, 0);
    const totalMedia = this.zonas.reduce((acc, z) => acc + z.desgloseSeveridad.media, 0);
    const totalCritica = this.zonas.reduce((acc, z) => acc + z.desgloseSeveridad.critica, 0);
    this.chart = new Chart(this.canvasRef.nativeElement, {
      type: 'doughnut',
      data: {
        labels: ['Baja', 'Media', 'Critica'],
        datasets: [{ data: [totalBaja, totalMedia, totalCritica], backgroundColor: ['#16A34A', '#F59E0B', '#DC2626'] }],
      },
      options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { position: 'bottom' } } },
    });
  }

  ngOnDestroy(): void {
    this.chart?.destroy();
  }
}
