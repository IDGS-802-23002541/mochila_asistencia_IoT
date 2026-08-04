export interface Proveedor {
  idProveedor: number;
  nombre: string;
  telefono: string;
  correo: string;
  direccion: string;
  activo: boolean;
  // Loa activan cuando se hace la relación con el proveedor, no es necesario que se muestre en la tabla de proveedores
  // materiasPrimas?: MateriaPrima[];
}