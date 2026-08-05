import { Component, OnInit, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { HttpClient, HttpClientModule } from '@angular/common/http';

interface Mensaje {
  emisor: 'bot' | 'usuario';
  texto: string;
  esResumen?: boolean;
}

// Desglose de costos reales que componen cada módulo.
// Todo en MXN. Esto es lo que hace que el precio "reaccione" a tus costos
// en lugar de ser un número fijo escrito a mano.
interface CostoDesglose {
  hardware: number;   // equipo, sensores, ESP32, baterías, GPS, etc.
  software: number;   // hosting, broker MQTT, procesamiento cloud
  personal: number;   // días-consultor / técnico en campo
  logistica: number;  // traslados, instalación, retiro de equipo
}

interface ModuloConsultoria {
  id: string;
  nombre: string;
  desc: string;
  tier: 'essential' | 'professional' | 'enterprise' | 'signal'; // color de marca
  imagen: string;
  agregado: boolean;
  costos: CostoDesglose;
  margen: number; // ej. 0.25 = 25% sobre el costo real
}

type TipoInstitucion = 'privada' | 'publica';

@Component({
  selector: 'app-quotation',
  standalone: true,
  imports: [CommonModule, FormsModule, HttpClientModule],
  templateUrl: './quotation.html',
  styleUrl: './quotation.scss',
})
export class Quotation implements OnInit {
  totalProyecto: number = 0;
  historialMensajes: Mensaje[] = [];
  mostrarPantallaLocalhost: boolean = false;

  correoUsuario: string = '';
  estaEnviando: boolean = false;
  errorRedDetectado: boolean = false;

  // Controla si cada tarjeta muestra su desglose de costos al cliente.
  // Índice alineado con modulosConsultoria.
  desglosesVisibles: boolean[] = [];

  // Tipo de institución: afecta el margen aplicado, no el costo real.
  tipoInstitucion: TipoInstitucion = 'privada';
  // Instituciones públicas reciben un margen reducido (no un costo reducido:
  // el costo real de sensores y personal no cambia, lo que cambia es cuánto
  // ganamos nosotros sobre ese costo).
  private factorMargenPorInstitucion: Record<TipoInstitucion, number> = {
    privada: 1,
    publica: 0.6,
  };

  private formspreeEndpoint = 'https://formspree.io/f/xaqryelv';

  esEmailValido(): boolean {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/;
    return emailRegex.test(this.correoUsuario);
  }

  modulosConsultoria: ModuloConsultoria[] = [
    {
      id: 'auditoria',
      nombre: 'Auditoría Física e Infraestructura Base',
      desc: 'Evaluación técnica inicial y mapeo de barreras arquitectónicas fijas en accesos principales y rutas críticas de desplazamiento.',
      tier: 'essential',
      imagen: 'https://images.unsplash.com/photo-1508313144761-0ea80db40091?auto=format&fit=crop&w=800&q=80',
      agregado: false,
      costos: { hardware: 1800, software: 700, personal: 14000, logistica: 3500 },
      margen: 0.25,
    },
    {
      id: 'iot',
      nombre: 'Monitoreo de Continuidad con Sensores IoT',
      desc: 'Despliegue temporal de hardware VisionGuard (sensores ultrasónicos y GPS) para registrar la continuidad real y obstáculos dinámicos por 2 semanas.',
      tier: 'professional',
      imagen: 'https://images.unsplash.com/photo-1555589228-135c25ae8cf5?auto=format&fit=crop&w=800&q=80',
      agregado: false,
      costos: { hardware: 12000, software: 3000, personal: 12000, logistica: 1000 },
      margen: 0.25,
    },
    {
      id: 'iaz',
      nombre: 'Cálculo del Índice de Accesibilidad (IAZ)',
      desc: 'Procesamiento analítico de la evidencia recolectada por los sensores mediante metodología KDD para construir el panorama del entorno.',
      tier: 'enterprise',
      imagen: 'https://images.unsplash.com/photo-1551288049-bebda4e38f71?auto=format&fit=crop&w=800&q=80',
      agregado: false,
      costos: { hardware: 0, software: 4000, personal: 8000, logistica: 0 },
      margen: 0.25,
    },
    {
      id: 'plan',
      nombre: 'Plan de Mitigación y Entrega Ejecutiva',
      desc: 'Desarrollo del plan maestro de adecuaciones institucionales y trazabilidad conforme a la Ley General de Educación Superior.',
      tier: 'signal',
      imagen: 'https://images.unsplash.com/photo-1758873269035-aae0e1fd3422?auto=format&fit=crop&w=800&q=80',
      agregado: false,
      costos: { hardware: 0, software: 1000, personal: 7000, logistica: 0 },
      margen: 0.25,
    },
  ];

  constructor(private http: HttpClient, private cdr: ChangeDetectorRef) {}

  ngOnInit() {
    this.desglosesVisibles = this.modulosConsultoria.map(() => false);
    this.actualizarMensajeAsistente();
  }

  // ---------- MOTOR DE PRECIOS ----------

  costoBase(item: ModuloConsultoria): number {
    const c = item.costos;
    return c.hardware + c.software + c.personal + c.logistica;
  }

  margenEfectivo(item: ModuloConsultoria): number {
    return item.margen * this.factorMargenPorInstitucion[this.tipoInstitucion];
  }

  // Precio final = costo real + margen (ajustado por tipo de institución),
  // redondeado a la centena para que se vea como una cotización, no una hoja de cálculo.
  precioFinal(item: ModuloConsultoria): number {
    const bruto = this.costoBase(item) * (1 + this.margenEfectivo(item));
    return Math.round(bruto / 100) * 100;
  }

  toggleDesglose(index: number): void {
    this.desglosesVisibles[index] = !this.desglosesVisibles[index];
  }

  cambiarTipoInstitucion(tipo: TipoInstitucion): void {
    if (this.tipoInstitucion === tipo) return;
    this.tipoInstitucion = tipo;
    this.recalcularTotal();
  }

  private recalcularTotal(): void {
    this.totalProyecto = this.modulosConsultoria
      .filter(m => m.agregado)
      .reduce((sum, m) => sum + this.precioFinal(m), 0);
    this.actualizarMensajeAsistente();
  }

  // ---------- FLUJO EXISTENTE (sin cambios de comportamiento) ----------

  toggleConcepto(index: number): void {
    const concepto = this.modulosConsultoria[index];
    concepto.agregado = !concepto.agregado;
    this.recalcularTotal();
  }

  actualizarMensajeAsistente() {
    this.errorRedDetectado = false;
    this.historialMensajes = [
      {
        emisor: 'bot',
        texto: '¡Hola! Selecciona las fases del proyecto en las tarjetas de abajo. Aquí verás el cálculo estimado en tiempo real bajo nuestro modelo de servitización.'
      }
    ];

    if (this.totalProyecto > 0) {
      this.historialMensajes.push({
        emisor: 'bot',
        texto: 'Perfecto. He procesado las fases seleccionadas para tu campus. Por favor, ingresa tu correo electrónico para procesar la cotización:',
        esResumen: true
      });
    }
  }

  async enviarCotizacionFinal(): Promise<void> {
    if (!this.esEmailValido()) {
      return;
    }

    this.estaEnviando = true;
    this.errorRedDetectado = false;
    this.cdr.detectChanges();

    const seleccionados = this.modulosConsultoria.filter(m => m.agregado);
    const serviciosElegidos = seleccionados.map(m => m.nombre).join(', ');
    const costoRealTotal = seleccionados.reduce((sum, m) => sum + this.costoBase(m), 0);

    const payload = new FormData();
    payload.append('email', this.correoUsuario);
    payload.append('proyecto', 'VisionGuard - Consultoría Institucional');
    payload.append('modulos_seleccionados', serviciosElegidos);
    payload.append('tipo_institucion', this.tipoInstitucion);
    payload.append('costo_real_total', `$${costoRealTotal} MXN`);
    payload.append('total_estimado', `$${this.totalProyecto} MXN`);

    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 4000);

    try {
      const response = await fetch(this.formspreeEndpoint, {
        method: 'POST',
        body: payload,
        headers: {
          'Accept': 'application/json'
        },
        signal: controller.signal
      });

      clearTimeout(timeoutId);
      this.estaEnviando = false;

      if (response.ok) {
        this.mostrarPantallaLocalhost = true;
      } else {
        throw new Error('Servidor remoto rechazó la petición');
      }

      this.cdr.detectChanges();

    } catch (err) {
      clearTimeout(timeoutId);
      this.estaEnviando = false;
      this.errorRedDetectado = true;
      this.mostrarPantallaLocalhost = true;
      this.cdr.detectChanges();
      console.warn('Fallo en comunicación externa o límite de tiempo excedido. Se activó el flujo local:', err);
    }
  }

  cerrarPantallaLocalhost(): void {
    this.mostrarPantallaLocalhost = false;
    this.totalProyecto = 0;
    this.correoUsuario = '';
    this.errorRedDetectado = false;
    this.modulosConsultoria.forEach(m => m.agregado = false);
    this.desglosesVisibles = this.modulosConsultoria.map(() => false);
    this.actualizarMensajeAsistente();
    this.cdr.detectChanges();
  }
}