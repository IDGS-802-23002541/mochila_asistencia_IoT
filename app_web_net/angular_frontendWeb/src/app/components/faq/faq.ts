import { Component, signal } from '@angular/core';
import { CommonModule } from '@angular/common';

interface FaqItem {
  id: string;
  question: string;
  answer: string;
}

@Component({
  selector: 'app-faq',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './faq.html',
  styleUrl: './faq.css'
})
export class Faq {
  openIds = signal<Set<string>>(new Set());

  items: FaqItem[] = [
    {
      id: 'cotizacion',
      question: '¿Cómo es el proceso de cotización?',
      answer:
        'Todo comienza desde el apartado de Cotización en nuestro sitio web. Ahí seleccionas el paquete que mejor se ajuste a las necesidades de tu institución, dejas tu correo de contacto y en breve un miembro del equipo de Vision Guard se pondrá en contacto contigo para afinar el alcance y enviarte una propuesta formal.'
    },
    {
      id: 'entregables',
      question: '¿Qué entregables recibo al finalizar el proyecto?',
      answer:
        'El entregable principal es un Reporte de Accesibilidad completo de tu institución. Incluye: portada con los metadatos del levantamiento (institución, periodo, rutas y recorridos cubiertos), un resumen ejecutivo con los hallazgos y zonas más críticas, la metodología aplicada (sensores utilizados, cálculo del Índice de Accesibilidad por Zona, umbrales y muestreo), un ranking de zonas por IAZ respaldado por el número de recorridos que sustenta cada dato, fichas detalladas de las zonas críticas con ubicación, severidad y narrativa del problema, una sección de cobertura y limitaciones que indica qué porcentaje del campus fue evaluado y qué zonas requieren más muestreo, y un anexo con la tabla completa de datos crudos y glosario de términos. El reporte documenta los patrones de accesibilidad; la decisión de qué intervención implementar queda en manos de la institución.'
    },
    {
      id: 'garantias',
      question: '¿Qué garantías ofrecen sobre el proyecto entregado?',
      answer:
        'Garantizamos que el reporte entregado refleja fielmente los datos recopilados durante el levantamiento, con la metodología y umbrales documentados de forma transparente. Si al revisar el entregable la institución identifica inconsistencias entre los datos de campo y el reporte final, ofrecemos una revisión sin costo adicional dentro de un periodo determinado tras la entrega.'
    },
    {
      id: 'contacto',
      question: '¿Cómo puedo agendar una llamada o reunión inicial?',
      answer:
        'Puedes hacerlo desde el apartado de Contáctanos en el sitio, donde podrás dejar tus datos y el motivo de tu solicitud para que el equipo de Vision Guard te contacte y agende una sesión inicial.'
    },
    {
      id: 'soporte',
      question: '¿Ofrecen soporte o mantenimiento después de entregado el proyecto?',
      answer:
        'Después de la entrega del reporte, el equipo de Vision Guard queda disponible para resolver dudas sobre su interpretación durante un periodo determinado. Si la institución requiere un nuevo levantamiento o actualización del diagnóstico más adelante, por ejemplo tras remodelaciones, puede contratarse como un proyecto de seguimiento independiente.'
    }
  ];

  toggle(id: string): void {
    this.openIds.update(current => {
      const next = new Set(current);
      if (next.has(id)) {
        next.delete(id);
      } else {
        next.add(id);
      }
      return next;
    });
  }

  isOpen(id: string): boolean {
    return this.openIds().has(id);
  }
}
