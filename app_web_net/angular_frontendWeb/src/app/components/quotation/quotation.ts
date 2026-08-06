import { Component, OnInit, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { HttpClient, HttpClientModule } from '@angular/common/http';

interface Mensaje {
  emisor: 'bot' | 'usuario';
  texto: string;
  esResumen?: boolean;
}

interface ModuloConsultoria {
  id: string;
  nombre: string;
  desc: string;
  precioTexto: string; // Texto estático del precio (ej: "$26,000 MXN")
  tier: 'essential' | 'professional' | 'enterprise' | 'signal';
  imagen: string;
  agregado: boolean;
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
  totalProyectoTexto: string = '$0 MXN';
  historialMensajes: Mensaje[] = [];
  mostrarPantallaLocalhost: boolean = false;

  correoUsuario: string = '';
  estaEnviando: boolean = false;
  errorRedDetectado: boolean = false;

  desglosesVisibles: boolean[] = [];
  tipoInstitucion: TipoInstitucion = 'privada';

  private formspreeEndpoint = 'https://formspree.io/f/xaqryelv';

  esEmailValido(): boolean {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/;
    return emailRegex.test(this.correoUsuario);
  }

  // Módulos con descripciones de m² y precios como TEXTO DIRECTO
  modulosConsultoria: ModuloConsultoria[] = [
    {
      id: 'auditoria',
      nombre: 'Access Insight',
      desc: 'Cobertura: Hasta 5,000 m². Evaluación técnica inicial y mapeo de barreras arquitectónicas fijas en accesos principales y rutas críticas.',
      precioTexto: '$26,000 MXN',
      tier: 'essential',
      imagen: 'https://images.unsplash.com/photo-1508313144761-0ea80db40091?auto=format&fit=crop&w=800&q=80',
      agregado: false,
    },
    {
      id: 'iot',
      nombre: 'Route Intelligence',
      desc: 'Cobertura: 5,000 m² a 15,000 m². Despliegue temporal de hardware VisionGuard para registrar la continuidad real y obstáculos dinámicos.',
      precioTexto: '$48,000 MXN',
      tier: 'professional',
      imagen: 'https://images.unsplash.com/photo-1555589228-135c25ae8cf5?auto=format&fit=crop&w=800&q=80',
      agregado: false,
    },
    {
      id: 'iaz',
      nombre: 'Smart Accessibility Analytics',
      desc: 'Cobertura: 15,000 m² a 30,000 m². Procesamiento analítico avanzado de la evidencia recolectada por los sensores mediante metodología KDD.',
      precioTexto: '$75,000 MXN',
      tier: 'enterprise',
      imagen: 'https://images.unsplash.com/photo-1551288049-bebda4e38f71?auto=format&fit=crop&w=800&q=80',
      agregado: false,
    },
    {
      id: 'plan',
      nombre: 'Strategic Accessibility Consulting',
      desc: 'Cobertura: Más de 30,000 m² (Campus Completo). Plan maestro de adecuaciones institucionales bajo la Ley General de Educación Superior.',
      precioTexto: '$110,000 MXN',
      tier: 'signal',
      imagen: 'https://images.unsplash.com/photo-1758873269035-aae0e1fd3422?auto=format&fit=crop&w=800&q=80',
      agregado: false,
    },
  ];

  constructor(private http: HttpClient, private cdr: ChangeDetectorRef) {}

  ngOnInit() {
    this.desglosesVisibles = this.modulosConsultoria.map(() => false);
    this.actualizarMensajeAsistente();
  }

  toggleDesglose(index: number): void {
    this.desglosesVisibles[index] = !this.desglosesVisibles[index];
  }

  cambiarTipoInstitucion(tipo: TipoInstitucion): void {
    if (this.tipoInstitucion === tipo) return;
    this.tipoInstitucion = tipo;
  }

  // ---------- SELECCIÓN ÚNICA DE PAQUETE ----------

  toggleConcepto(index: number): void {
    const estabaAgregado = this.modulosConsultoria[index].agregado;

    // 1. Desmarcamos todos los paquetes
    this.modulosConsultoria.forEach(m => m.agregado = false);

    // 2. Si no estaba marcado, lo marcamos y tomamos directamente su texto de precio
    if (!estabaAgregado) {
      this.modulosConsultoria[index].agregado = true;
      this.totalProyectoTexto = this.modulosConsultoria[index].precioTexto;
    } else {
      this.totalProyectoTexto = '$0 MXN';
    }

    this.actualizarMensajeAsistente();
  }

  actualizarMensajeAsistente() {
    this.errorRedDetectado = false;
    this.historialMensajes = [
      {
        emisor: 'bot',
        texto: '¡Hola! Selecciona el paquete que mejor se adapte a tu proyecto para visualizar el presupuesto estimado en tiempo real.'
      }
    ];

    if (this.totalProyectoTexto !== '$0 MXN') {
      this.historialMensajes.push({
        emisor: 'bot',
        texto: 'Perfecto. He procesado la fase seleccionada para tu campus. Por favor, ingresa tu correo electrónico para solicitar la cotización formal:',
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

    const seleccionado = this.modulosConsultoria.find(m => m.agregado);
    const servicioElegido = seleccionado ? seleccionado.nombre : 'Sin Selección';

    const payload = new FormData();
    payload.append('email', this.correoUsuario);
    payload.append('proyecto', 'VisionGuard - Consultoría Institucional');
    payload.append('modulos_seleccionados', servicioElegido);
    payload.append('tipo_institucion', this.tipoInstitucion);
    payload.append('total_estimado', this.totalProyectoTexto);

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
    this.totalProyectoTexto = '$0 MXN';
    this.correoUsuario = '';
    this.errorRedDetectado = false;
    this.modulosConsultoria.forEach(m => m.agregado = false);
    this.desglosesVisibles = this.modulosConsultoria.map(() => false);
    this.actualizarMensajeAsistente();
    this.cdr.detectChanges();
  }
}