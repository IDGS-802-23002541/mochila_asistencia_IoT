import { ZonaAccesibilidad } from '../models/zona-accesibilidad.model';

// Datos reales: output del pipeline (DBSCAN + IAZ) corrido sobre el mock v5
// en cangurera_local (tickets 003.4/004/004.2), generados con
// generar_json_zonas() y verificados matematicamente contra Zonas_IAZ.
// Cuando exista un endpoint real del backend, este archivo se reemplaza
// por un fetch() en tiempo de ejecucion, sin tocar el resto del modulo.
export const ZONAS_MOCK: ZonaAccesibilidad[] = [
  {
    zonaId: 'Zona 1',
    lat: 21.06328, lon: -101.579521, radioMetros: 12,
    iaz: 12.0,
    cantidadEventos: 16,
    cantidadRecorridosQueCruzaron: 3,
    nivelAccesibilidad: 'Baja',
    tipoEventoPredominante: 'Obstaculo',
    desgloseSeveridad: { baja: 9, media: 4, critica: 3 },
    desglosePorTipoEvento: [
      { tipoEvento: 'Caida_Detectada', cantidad: 3, severidadPredominante: 'Critica' },
      { tipoEvento: 'Obstaculo', cantidad: 9, severidadPredominante: 'Baja' },
      { tipoEvento: 'Tropiezo', cantidad: 4, severidadPredominante: 'Media' },
    ],
    fechaUltimaActualizacion: '2026-07-28T21:13:31.646879',
  },
  {
    zonaId: 'Zona 0',
    lat: 21.062358, lon: -101.579416, radioMetros: 12,
    iaz: 10.3333,
    cantidadEventos: 15,
    cantidadRecorridosQueCruzaron: 3,
    nivelAccesibilidad: 'Baja',
    tipoEventoPredominante: 'Obstaculo',
    desgloseSeveridad: { baja: 9, media: 4, critica: 2 },
    desglosePorTipoEvento: [
      { tipoEvento: 'Caida_Detectada', cantidad: 2, severidadPredominante: 'Critica' },
      { tipoEvento: 'Obstaculo', cantidad: 9, severidadPredominante: 'Baja' },
      { tipoEvento: 'Tropiezo', cantidad: 4, severidadPredominante: 'Media' },
    ],
    fechaUltimaActualizacion: '2026-07-28T21:13:31.656506',
  },
  {
    zonaId: 'Zona 2',
    lat: 21.064193, lon: -101.583081, radioMetros: 12,
    iaz: 6.5,
    cantidadEventos: 13,
    cantidadRecorridosQueCruzaron: 6,
    nivelAccesibilidad: 'Baja',
    tipoEventoPredominante: 'Caida_Detectada',
    desgloseSeveridad: { baja: 5, media: 3, critica: 5 },
    desglosePorTipoEvento: [
      { tipoEvento: 'Caida_Detectada', cantidad: 5, severidadPredominante: 'Critica' },
      { tipoEvento: 'Obstaculo', cantidad: 5, severidadPredominante: 'Baja' },
      { tipoEvento: 'Tropiezo', cantidad: 3, severidadPredominante: 'Media' },
    ],
    fechaUltimaActualizacion: '2026-07-28T21:13:31.671377',
  },
  {
    zonaId: 'Zona 3',
    lat: 21.062635, lon: -101.578255, radioMetros: 12,
    iaz: 4.0,
    cantidadEventos: 4,
    cantidadRecorridosQueCruzaron: 3,
    nivelAccesibilidad: 'Media',
    tipoEventoPredominante: 'Caida_Detectada',
    desgloseSeveridad: { baja: 2, media: 0, critica: 2 },
    desglosePorTipoEvento: [
      { tipoEvento: 'Caida_Detectada', cantidad: 2, severidadPredominante: 'Critica' },
      { tipoEvento: 'Obstaculo', cantidad: 2, severidadPredominante: 'Baja' },
    ],
    fechaUltimaActualizacion: '2026-07-28T21:13:31.678803',
  },
];
