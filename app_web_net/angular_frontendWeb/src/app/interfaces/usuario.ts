export interface Usuario {
  id: number;
  organizacionId: number;
  nombre: string;
  correo: string;
  contrasena_Hash: string;
  rol: string;
  fechaRegistro: string;
  fotoUrl: string | null;
  estado_Activo: boolean;
}
