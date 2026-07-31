export interface Dispositivo {
  id: number;
  organizacionId: number;
  macAddress: string;
  estado: string;
  ultimaConexion: string | null;
  fechaRegistro: string;
  organizacion: string | null;
}