export interface Comentario {
  idComentario: number;
  nombreCliente: string;
  correoCliente: string;
  mensaje: string;
  fechaCreacion: string;
  estado: 'Pendiente' | 'EnRevision' | 'Atendido';
  respuestaAdministrador?: string;
  fechaRespuesta?: string;
}

export interface CrearComentarioDto {
  nombreCliente: string;
  correoCliente: string;
  mensaje: string;
  idProducto?: number;
  calificacion?: number;
}
export interface ActualizarComentarioDto {
  estado: string;
  respuestaAdministrador?: string;
}
