import { ZonaAccesibilidad } from '../models/zona-accesibilidad.model';

export const ZONAS_MOCK: ZonaAccesibilidad[] = [
  { zonaId: 'Z-01 Entrada Principal', lat: 21.06262, lon: -101.581889, radioMetros: 15, iaz: 6.8, cantidadEventos: 34, cantidadRecorridosQueCruzaron: 22, tipoEventoPredominante: 'Alto', desglose: { bajo: 4, medio: 10, alto: 20 } },
  { zonaId: 'Z-02 Estacionamiento 1', lat: 21.06419, lon: -101.584016, radioMetros: 20, iaz: 5.1, cantidadEventos: 28, cantidadRecorridosQueCruzaron: 25, tipoEventoPredominante: 'Medio', desglose: { bajo: 6, medio: 16, alto: 6 } },
  { zonaId: 'Z-03 Pasillo Central', lat: 21.063279, lon: -101.57953, radioMetros: 12, iaz: 2.3, cantidadEventos: 15, cantidadRecorridosQueCruzaron: 30, tipoEventoPredominante: 'Bajo', desglose: { bajo: 10, medio: 4, alto: 1 } },
  { zonaId: 'Z-04 Estacionamiento 2', lat: 21.062353, lon: -101.579416, radioMetros: 18, iaz: 4.6, cantidadEventos: 21, cantidadRecorridosQueCruzaron: 24, tipoEventoPredominante: 'Medio', desglose: { bajo: 5, medio: 12, alto: 4 } },
  { zonaId: 'Z-05 Acceso Biblioteca', lat: 21.063788, lon: -101.581147, radioMetros: 10, iaz: 1.4, cantidadEventos: 8, cantidadRecorridosQueCruzaron: 27, tipoEventoPredominante: 'Bajo', desglose: { bajo: 6, medio: 2, alto: 0 } },
  { zonaId: 'Z-06 Estacionamiento 3', lat: 21.062636, lon: -101.578256, radioMetros: 20, iaz: 3.9, cantidadEventos: 18, cantidadRecorridosQueCruzaron: 21, tipoEventoPredominante: 'Medio', desglose: { bajo: 4, medio: 11, alto: 3 } },
];
