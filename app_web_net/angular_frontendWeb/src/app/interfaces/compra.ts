export interface DetalleCompraCreate {
  idMateriaPrima: number;
  cantidad: number;
  precioUnitario: number;
}

export interface CompraCreateDto {
  idProveedor: number;
  fechaCompra?: string;
  detalles: DetalleCompraCreate[];
}

export interface DetalleCompraResponse {
  idDetalleCompra: number;
  idMateriaPrima: number;
  nombreMateriaPrima: string;
  cantidad: number;
  precioUnitario: number;
  subtotal: number;
}

export interface Compra {
  idCompra: number;
  fechaCompra: string;
  idProveedor: number;
  nombreProveedor: string;
  total: number;
  detalles: DetalleCompraResponse[];
}