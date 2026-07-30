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
  // FIX (contrato JSON, ticket pendiente contrato mapa-calor): reemplaza
  // el severidadPredominante de nivel-zona que existia antes. Ese campo
  // salia de "cual severidad es mas frecuente entre los eventos", pero
  // lo que el equipo decidio usar es nivelAccesibilidad (Alta/Media/Baja),
  // derivado del IAZ con los umbrales fijos confirmados en ticket 004.2
  // (IAZ<3 Alta, 3-6 Media, >=6 Baja). El severidadPredominante POR TIPO
  // de evento (dentro de desglosePorTipoEvento) SI se conserva, es un
  // dato distinto y sigue siendo util.
  nivelAccesibilidad: 'Alta' | 'Media' | 'Baja';
  tipoEventoPredominante: string;
  desgloseSeveridad: DesgloseSeveridad;
  desglosePorTipoEvento: DesgloseTipoEvento[];
  fechaUltimaActualizacion: string;
}
