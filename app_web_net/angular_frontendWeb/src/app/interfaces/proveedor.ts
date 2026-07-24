export interface Proveedor {
  id: number;
  nombre: string;
  estado_Activo: boolean;
  contacto_Principal: string | number;
  telefono: string | number;
  email_Contacto: string | number;
  direccion: string | number;
}

export interface ProveedorResumen {
  id: number;
  nombre: string;
  estado_Activo: boolean;
}
