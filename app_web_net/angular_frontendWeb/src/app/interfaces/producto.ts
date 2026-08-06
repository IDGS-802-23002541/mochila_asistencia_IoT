export interface MateriaPrima {
  idMateriaPrima: number;
  nombre: string;
  descripcion?: string | null;
  costoUnitario: number;
  stock: number;
  stockMinimo: number;
  idProveedor: number;
}

export interface RecetaItem {
  idMateriaPrima: number;
  cantidad: number; // piezas
}

export interface RecetaDetalleItem {
  idMateriaPrima: number;
  nombreMateriaPrima: string;
  cantidad: number; // piezas
  costoUnitario: number;
}
export interface ProductoResumen {
  idProducto: number;
  nombre: string;
  activo: boolean;
}
export interface Producto {
  idProducto: number;
  nombre: string;
  descripcion?: string | null;
  precio: number;
  stock: number;
  margenGanancia: number;
  activo: boolean;
  fotoUrl?: string | null;
}

export interface ProductoDetalle extends Producto {
  receta: RecetaDetalleItem[];
}

export interface ProductoCreateDto {
  nombre: string;
  descripcion?: string | null;
  precio: number;
  stock: number;
  margenGanancia: number;
  activo: boolean;
  fotoUrl?: string | null;
  receta: RecetaItem[];
}
