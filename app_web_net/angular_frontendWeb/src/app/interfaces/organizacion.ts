/** Matches CangureraInteligente.Models.Organizacion (public/serialized shape) */
export interface Organizacion {
  id: number;
  nombre: string;
  sector: string;
  contacto_Principal?: string | null;
  email_Contacto?: string | null;
  fechaCreacion?: string;
  fotoUrl?: string | null;
  estado_Activo: boolean;
  contrasena_Hash?: string | null;
  rol: string;
  es_Interna: boolean;
}

/** Forma del formulario de creación: sin id/fechaCreacion, que los pone el backend. */
export type NuevaOrganizacion = Omit<Organizacion, 'id' | 'fechaCreacion'>;
