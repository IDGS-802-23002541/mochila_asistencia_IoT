export interface MateriaPrima {
  id: number;
  nombre: string;
  estado_Activo: boolean;
  categoria: string | number;
  unidad_Medida: string | number;
  stock_Actual: string | number;
  precio_Unitario: string | number;
  proveedor: string | number;
}

export interface MateriaPrimaResumen {
  id: number;
  nombre: string;
  estado_Activo: boolean;
}
