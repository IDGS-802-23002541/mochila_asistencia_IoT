export interface ZonaAccesibilidad {
  zonaId: string;
  lat: number;
  lon: number;
  radioMetros: number;
  iaz: number;
  cantidadEventos: number;
  cantidadRecorridosQueCruzaron: number;
  tipoEventoPredominante: 'Bajo' | 'Medio' | 'Alto';
  desglose: { bajo: number; medio: number; alto: number };
}
