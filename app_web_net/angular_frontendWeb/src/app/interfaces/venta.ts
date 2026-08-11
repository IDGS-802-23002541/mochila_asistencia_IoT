export interface DetalleVentaItem {
  idDetalleVenta: number;
  idVenta: number;
  idProducto: number;
  cantidad: number;
  precioUnitario: number;
  producto?: {
    idProducto: number;
    nombre: string;
    fotoUrl?: string | null;
  } | null;
}

export interface Venta {
  idVenta: number;
  fechaVenta: string;
  total: number;
  idOrganizacion: number;
  detalles: DetalleVentaItem[];
}

export interface VentaCreateDto {
  idOrganizacion: number;
  detalles: { idProducto: number; cantidad: number }[];
}