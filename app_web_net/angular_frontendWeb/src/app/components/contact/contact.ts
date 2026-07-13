import { Component, ChangeDetectorRef, ViewEncapsulation } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';

@Component({
  selector: 'app-contact',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './contact.html',
  styleUrl: './contact.css',
  encapsulation: ViewEncapsulation.None
})
export class Contact {
  nombreUsuario: string = '';
  correoUsuario: string = '';
  telefonoUsuario: string = '';
  mensajeUsuario: string = '';

  estaEnviando: boolean = false;
  errorRedDetectado: boolean = false;
  mostrarPantallaLocalhost: boolean = false;

  private formspreeEndpoint = 'https://formspree.io/f/xaqryelv';

  constructor(private cdr: ChangeDetectorRef) {}

  esEmailValido(): boolean {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/;
    return emailRegex.test(this.correoUsuario);
  }

  async enviarContacto(): Promise<void> {
    if (!this.esEmailValido() || !this.nombreUsuario) {
      return;
    }

    // ACCIÓN INMEDIATA: Mostramos la pantalla emergente sin esperar al servidor
    this.estaEnviando = false;
    this.errorRedDetectado = false;
    this.mostrarPantallaLocalhost = true;

    // Forzar renderizado instantáneo en el mismo milisegundo del clic
    this.cdr.detectChanges();

    // Empaquetamos el payload en segundo plano
    const payload = new FormData();
    payload.append('nombre', this.nombreUsuario);
    payload.append('email', this.correoUsuario);
    payload.append('telefono', this.telefonoUsuario || 'No proporcionado');
    payload.append('mensaje', this.mensajeUsuario || 'Sin contenido adicional');
    payload.append('origen_formulario', 'Formulario de Contacto General');

    // Lanzamos la petición de red asíncrona "Fire-and-Forget" (Disparar y continuar)
    fetch(this.formspreeEndpoint, {
      method: 'POST',
      body: payload,
      headers: { 'Accept': 'application/json' }
    })
    .then(response => {
      if (!response.ok) {
        // Si el servidor rechaza, marcamos el error en el modal de fondo de forma reactiva
        this.errorRedDetectado = true;
        this.cdr.detectChanges();
      }
    })
    .catch(err => {
      // Si hay un bloqueo por Adblock o CORS en segundo plano, actualizamos el modal de inmediato
      this.errorRedDetectado = true;
      this.cdr.detectChanges();
      console.warn('Intercepción local activa en segundo plano:', err);
    });
  }

  cerrarPantallaLocalhost(): void {
    this.mostrarPantallaLocalhost = false;
    this.nombreUsuario = '';
    this.correoUsuario = '';
    this.telefonoUsuario = '';
    this.mensajeUsuario = '';
    this.errorRedDetectado = false;
    this.cdr.detectChanges(); // Renderizado instantáneo al limpiar
  }
}
