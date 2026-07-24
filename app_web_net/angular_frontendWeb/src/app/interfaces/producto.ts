export interface Producto {
  id: number;
  nombre: string;
  estado_Activo: boolean;
  categoria: string | number;
  precio: string | number;
  stock: string | number;
  descripcion: string | number;
}

export interface ProductoResumen {
  id: number;
  nombre: string;
  estado_Activo: boolean;
}
