export interface Proveedor {
  idProveedor: number;
  nombre: string;
}

export interface MateriaPrimaResumen {
  idMateriaPrima: number;
  nombre: string;
  stock: number;
  stockMinimo: number;
}

export interface MateriaPrima {
  idMateriaPrima: number;
  nombre: string;
  descripcion?: string | null;
  costoUnitario: number;
  precioPromedio?: number | null;
  stock: number;
  stockMinimo: number;
  idProveedor: number;
  proveedor?: Proveedor | null;
}

// Lo que se envía en POST/PUT api/materias-primas
export interface MateriaPrimaCreateDto {
  nombre: string;
  descripcion?: string | null;
  costoUnitario: number;
  stock: number;
  stockMinimo: number;
  idProveedor: number;
}
