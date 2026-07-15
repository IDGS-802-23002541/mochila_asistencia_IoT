import { Component, OnInit, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { HttpClient, HttpClientModule } from '@angular/common/http';

interface Mensaje {
  emisor: 'bot' | 'usuario';
  texto: string;
  esResumen?: boolean;
}

@Component({
  selector: 'app-quotation',
  standalone: true,
  imports: [CommonModule, FormsModule, HttpClientModule],
  templateUrl: './quotation.html',
  styleUrl: './quotation.css',
})
export class Quotation implements OnInit {
  totalProyecto: number = 0;
  historialMensajes: Mensaje[] = [];
  mostrarPantallaLocalhost: boolean = false;

  correoUsuario: string = '';
  estaEnviando: boolean = false;

  // Flag para notificar al usuario de un bloqueo local de red (CORS, Adblock)
  errorRedDetectado: boolean = false;

  // Tu endpoint activo de Formspree
  private formspreeEndpoint = 'https://formspree.io/f/xaqryelv';

  // Regex ultra-flexible para soportar dominios institucionales como .edu.mx sin atorarse
  esEmailValido(): boolean {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/;
    return emailRegex.test(this.correoUsuario);
  }

  modulosConsultoria = [
    {
      id: 'auditoria',
      nombre: 'Auditoría Física e Infraestructura Base',
      precio: 25000,
      desc: 'Evaluación técnica inicial y mapeo de barreras arquitectónicas fijas en accesos principales y rutas críticas de desplazamiento.',
      imagen: 'https://images.unsplash.com/photo-1576765608535-5f04d1e3f289?auto=format&fit=crop&w=600&q=80',
      agregado: false
    },
    {
      id: 'iot',
      nombre: 'Monitoreo de Continuity con Sensores IoT',
      precio: 35000,
      desc: 'Despliegue temporal de hardware VisionGuard (sensores ultrasónicos y GPS) para registrar la continuidad real y obstáculos dinámicos por 2 semanas.',
      imagen: 'https://images.unsplash.com/photo-1518770660439-4636190af475?auto=format&fit=crop&w=600&q=80',
      agregado: false
    },
    {
      id: 'iaz',
      nombre: 'Cálculo del Índice de Accesibilidad (IAZ)',
      precio: 15000,
      desc: 'Procesamiento analítico descriptivo de la evidencia recolectada por los sensores para construir un panorama del estado del entorno.',
      imagen: 'https://images.unsplash.com/photo-1551288049-bebda4e38f71?auto=format&fit=crop&w=600&q=80',
      agregado: false
    },
    {
      id: 'plan',
      nombre: 'Plan de Mitigación y Entrega Ejecutiva',
      precio: 10000,
      desc: 'Desarrollo del plan maestro de adecuaciones institucionales y trazabilidad de acuerdo a las normativas de la Ley General de Educación Superior.',
      imagen: 'https://images.unsplash.com/photo-1503387762-592deb58ef4e?auto=format&fit=crop&w=600&q=80',
      agregado: false
    }
  ];

  // Inyectamos ChangeDetectorRef para forzar actualizaciones visuales inmediatas
  constructor(private http: HttpClient, private cdr: ChangeDetectorRef) {}

  ngOnInit() {
    this.actualizarMensajeAsistente();
  }

  toggleConcepto(index: number): void {
    const concepto = this.modulosConsultoria[index];
    concepto.agregado = !concepto.agregado;

    if (concepto.agregado) {
      this.totalProyecto += concepto.precio;
    } else {
      this.totalProyecto -= concepto.precio;
    }

    this.actualizarMensajeAsistente();
  }

  actualizarMensajeAsistente() {
    this.errorRedDetectado = false; // Resetear error
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
    this.cdr.detectChanges(); // Forzar estado de "Enviando..." en la UI al instante

    const serviciosElegidos = this.modulosConsultoria
      .filter(m => m.agregado)
      .map(m => m.nombre)
      .join(', ');

    const payload = new FormData();
    payload.append('email', this.correoUsuario);
    payload.append('proyecto', 'VisionGuard - Consultoría Institucional');
    payload.append('modulos_seleccionados', serviciosElegidos);
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

      // ¡CRÍTICO! Forzar a Angular a renderizar el modal inmediatamente
      this.cdr.detectChanges();

    } catch (err) {
      clearTimeout(timeoutId);
      this.estaEnviando = false;
      this.errorRedDetectado = true;
      this.mostrarPantallaLocalhost = true;

      // Forzar a Angular a renderizar el estado de error/localhost inmediatamente
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
    this.actualizarMensajeAsistente();
    this.cdr.detectChanges(); // Forzar limpieza de pantalla al cerrar
  }
}
