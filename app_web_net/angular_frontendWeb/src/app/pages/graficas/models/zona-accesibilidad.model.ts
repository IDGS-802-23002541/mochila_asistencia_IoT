export interface DesgloseSeveridad {
  baja: number;
  media: number;
  critica: number;
}

export interface DesgloseTipoEvento {
  tipoEvento: string;
  cantidad: number;
  severidadPredominante: 'Baja' | 'Media' | 'Critica';
}

export interface ZonaAccesibilidad {
  zonaId: string;
  lat: number;
  lon: number;
  radioMetros: number;
  iaz: number;
  cantidadEventos: number;
  cantidadRecorridosQueCruzaron: number;
  severidadPredominante: 'Baja' | 'Media' | 'Critica';
  tipoEventoPredominante: string;
  desgloseSeveridad: DesgloseSeveridad;
  desglosePorTipoEvento: DesgloseTipoEvento[];
  fechaUltimaActualizacion: string;
}
