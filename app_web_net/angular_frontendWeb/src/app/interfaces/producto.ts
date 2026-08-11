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
  incluyeMochila: boolean;
}

export interface ContenidoDetalle {
  idProductoContenido: number;
  idItem: number;
  nombreItem: string;
  cantidad: number;
}

export interface DocumentoArchivo {
  idProductoDocumento: number;
  nombreArchivo: string;
  tipoContenido: string;
  descripcion?: string | null;
  fechaSubida: string;
}

export interface ProductoDetalle extends Producto {
  contenido: ContenidoDetalle[];
  documentos: DocumentoArchivo[];
  receta: RecetaDetalleItem[];
}

// Detalle que recibe el cliente (sin receta, costos ni stock).
export interface ProductoPublico {
  idProducto: number;
  nombre: string;
  descripcion?: string | null;
  precio: number;
  fotoUrl?: string | null;
  incluyeMochila: boolean;
  contenido: ContenidoDetalle[];
  documentos: DocumentoArchivo[];
}

export interface ProductoCreateDto {
  nombre: string;
  descripcion?: string | null;
  precio: number;
  stock: number;
  margenGanancia: number;
  activo: boolean;
  fotoUrl?: string | null;
  incluyeMochila?: boolean;
  receta: RecetaItem[];
}

export interface DocumentoCreateDto {
  nombreArchivo: string;
  tipoContenido: string;
  descripcion?: string | null;
  contenidoBase64: string;
}

export interface ContenidoItem {
  idItem: number;
  cantidad: number;
}
