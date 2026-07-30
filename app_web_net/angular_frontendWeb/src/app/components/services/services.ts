import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-services',
  standalone: true,
  imports: [ CommonModule],
  templateUrl: './services.html',
  styleUrl: './services.css',
})
export class Services {
  showPanel: boolean = false;
  selectedPackage: any = {
    title: '',
    description: '',
    includes: [],
    benefits: []
  };

  // Para el menejo de los paquetes utilice un objeto con
  // las propiedades de cada paquete, esto permite agregar o modificar paquetes de
  //  manera más sencilla y mantener el código más limpio.
  packages: any = {
    1: {
      title: 'Diagnóstico Inicial de Accesibilidad',
      description:
      'Evaluamos la infraestructura educativa mediante recorridos reales para identificar barreras que afectan la movilidad de personas con discapacidad visual.',
      includes: [
        'Recorridos físicos dentro de la institución',
        'Identificación de obstáculos',
        'Evaluación de rutas principales',
        'Informe inicial de accesibilidad'
      ],
      benefits: [
        'Detectar problemas actuales',
        'Conocer zonas críticas',
        'Planificar mejoras futuras'
      ]
    },

    2: {
      title: 'Evaluación con Tecnología IoT',
      description:
      'Utilizamos sensores inteligentes para recopilar información objetiva sobre obstáculos, rutas y condiciones del entorno durante los recorridos.',
      includes: [
        'Uso de sensores inteligentes IoT',
        'Captura de datos en tiempo real',
        'Análisis de obstáculos',
        'Reporte tecnológico'
      ],


      benefits: [
        'Información precisa del entorno',
        'Evaluación basada en datos',
        'Mayor control de accesibilidad'
      ]
    },

    3: {
      title: 'Índice de Accesibilidad por Zona',
      description:
      'Generamos indicadores que permiten conocer el nivel de accesibilidad de cada área evaluada para facilitar la toma de decisiones.',
     includes: [
        'Evaluación por zonas',
        'Indicadores de accesibilidad',
        'Clasificación de áreas',
        'Identificación de puntos críticos'
      ],
      benefits: [
        'Permite comparar espacios',
        'Facilita la planificación',
        'Ayuda a priorizar mejoras'
      ]
    },

    4: {
      title: 'Consultoría Integral en Accesibilidad',
      description:
      'Entregamos un informe técnico con recomendaciones para implementar mejoras orientadas a la inclusión y movilidad autónoma.',
      includes: [
        'Diagnóstico completo',
        'Evaluación con tecnología IoT',
        'Informe técnico especializado',
        'Recomendaciones de mejora'
      ],


      benefits: [
        'Espacios educativos más inclusivos',
        'Mayor autonomía de usuarios',
        'Plan de mejora personalizado'
      ]
    }
  };

  openPanel(id: number) {
    this.selectedPackage = this.packages[id];
    this.showPanel = true;
  }
  closePanel() {
    this.showPanel = false;
  }
}
