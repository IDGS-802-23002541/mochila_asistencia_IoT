-- =====================================================================
-- DATASET DE PRUEBA - Proveedores, Materia Prima, Productos y Compras
-- Tablas del esquema Operativo. Ejecutar SOLO UNA VEZ (tablas vacias).
-- Sin USE, sin GO. Cada sentencia se ejecuta de forma independiente.
-- =====================================================================

-- ---------------------------------------------------------------------
-- 1. PROVEEDORES
-- ---------------------------------------------------------------------
SET IDENTITY_INSERT Operativo.Proveedores ON;

INSERT INTO Operativo.Proveedores (IdProveedor, Nombre, Telefono, Correo, Direccion, Activo) VALUES
(1, N'Distribuidora Industrial del Bajío',    N'477-100-2030', N'ventas@dibajio.mx',      N'Av. Industria 1120, León, Gto.', 1);
INSERT INTO Operativo.Proveedores (IdProveedor, Nombre, Telefono, Correo, Direccion, Activo) VALUES
(2, N'Textiles del Centro',                    N'477-905-5540', N'contacto@textilescrow.mx',  N'Blvd. Torres Landa 450, León, Gto.',   1);
INSERT INTO Operativo.Proveedores (IdProveedor, Nombre, Telefono, Correo, Direccion, Activo) VALUES
(3, N'Electrónicos IoT México',                N'442-228-1177', N'ventas@iotmx.mx',        'Av. Tecnológico 255, Querétaro, Qro.',   1);
INSERT INTO Operativo.Proveedores (IdProveedor, Nombre, Telefono, Correo, Direccion, Activo) VALUES
(4, N'Plásticos y Polimeros MX',              N'555-449-9031', N'pedidos@plasticosmx.mx',  'Calle 20 de Noviembre 34, CDMX',         1);
INSERT INTO Operativo.Proveedores (IdProveedor, Nombre, Telefono, Correo, Direccion, Activo) VALUES
(5, N'Ferreteria Industrial León',              N'477-712-6600', N'ventas@ferreteraleon.mx', 'Av. López Mateos 501, León, Gto.',       1);
INSERT INTO Operativo.Proveedores (IdProveedor, Nombre, Telefono, Correo, Direccion, Activo) VALUES
(6, N'Componentes y Módulos Smart',             N'818-310-5540', N'contacto@smartcomp.mx',   'Av. Industrias 7, Guadalupe, N.L.',      1);
INSERT INTO Operativo.Proveedores (IdProveedor, Nombre, Telefono, Correo, Direccion, Activo) VALUES
(7, N'Telecomunicaciones Alameda',              N'477-410-8821', N'ventas@telealameda.mx',    'Calzada de las Armas 150, León, Gto.',   1);
INSERT INTO Operativo.Proveedores (IdProveedor, Nombre, Telefono, Correo, Direccion, Activo) VALUES
(8, N'Texturas y Accesorios GDL',               N'333-314-7725', N'pedidos@texturasgdl.mx',  'Av. Federalismo 410, Guadalajara, Jal.', 0);

SET IDENTITY_INSERT Operativo.Proveedores OFF;

-- ---------------------------------------------------------------------
-- 2. MATERIA PRIMA
-- ---------------------------------------------------------------------
SET IDENTITY_INSERT Operativo.MateriaPrima ON;

INSERT INTO Operativo.MateriaPrima (IdMateriaPrima, Nombre, Descripcion, CostoUnitario, Stock, StockMinimo, IdProveedor) VALUES
(1, N'Tela de algodón reforzada', N'Tela 500g/m2 para la mochila. Rollo de 25m.', 14.50, 800,  100, 1);
INSERT INTO Operativo.MateriaPrima (IdMateriaPrima, Nombre, Descripcion, CostoUnitario, Stock, StockMinimo, IdProveedor) VALUES
(2, N'Hilo de coser reforzado',   N'Carrete de hilo especial para carga.',        2.50,  250,  60,  2);
INSERT INTO Operativo.MateriaPrima (IdMateriaPrima, Nombre, Descripcion, CostoUnitario, Stock, StockMinimo, IdProveedor) VALUES
(3, N'Cierre metálico',            N'Cierre YKK 50cm con doble cursor.',          2.80,  400,  80,  1);
INSERT INTO Operativo.MateriaPrima (IdMateriaPrima, Nombre, Descripcion, CostoUnitario, Stock, StockMinimo, IdProveedor) VALUES
(4, N'Espuma de protección',        N'Espuma EVA 5mm para los compartimentos.',    13.00, 350,  70,  4);
INSERT INTO Operativo.MateriaPrima (IdMateriaPrima, Nombre, Descripcion, CostoUnitario, Stock, StockMinimo, IdProveedor) VALUES
(5, N'Cable USB-C flexible',        N'Cable trenzado 1.2m con encapsulado.',       8.50,  450,  100, 8);
INSERT INTO Operativo.MateriaPrima (IdMateriaPrima, Nombre, Descripcion, CostoUnitario, Stock, StockMinimo, IdProveedor) VALUES
(6, N'Microcontrolador ESP32',      N'Wi-Fi + BLE para el registro de asistencia.', 95.00, 120,  40,  3);
INSERT INTO Operativo.MateriaPrima (IdMateriaPrima, Nombre, Descripcion, CostoUnitario, Stock, StockMinimo, IdProveedor) VALUES
(7, N'Batería LiPo 3.7V 1200mAh',   N'Con protección overcharge.',               42.00,  220,  50,  3);
INSERT INTO Operativo.MateriaPrima (IdMateriaPrima, Nombre, Descripcion, CostoUnitario, Stock, StockMinimo, IdProveedor) VALUES
(8, N'Módulo RFID RC522',           N'Lector/escritor RFID 13.56MHz.',            24.00, 160,  40,  6);
INSERT INTO Operativo.MateriaPrima (IdMateriaPrima, Nombre, Descripcion, CostoUnitario, Stock, StockMinimo, IdProveedor) VALUES
(9, N'Módulo SIM808',               N'GSM/GPRS para alertas de emergencia.',       26.00, 70,   15,  6);
INSERT INTO Operativo.MateriaPrima (IdMateriaPrima, Nombre, Descripcion, CostoUnitario, Stock, StockMinimo, IdProveedor) VALUES
(10, N'Cinta reflectante 3M',        N'Rollo 5cm x 45m de seguridad nocturna.',     2.00,  700,  200, 8);

SET IDENTITY_INSERT Operativo.MateriaPrima OFF;

-- ---------------------------------------------------------------------
-- 3. PRODUCTOS (con receta en ProductoMateriaPrima)
-- ---------------------------------------------------------------------
SET IDENTITY_INSERT Operativo.Productos ON;

INSERT INTO Operativo.Productos (IdProducto, Nombre, Descripcion, Precio, Stock, MargenGanancia, Activo, FotoUrl) VALUES
(1, N'Mochila Vision Guard Scout',  N'Modelo básico con sensor de caída.',      1250.00, 25,  25.00, 1, NULL);
INSERT INTO Operativo.Productos (IdProducto, Nombre, Descripcion, Precio, Stock, MargenGanancia, Activo, FotoUrl) VALUES
(2, N'Mochila Vision Guard Pro',    N'Modelo intermedio con GPS y alerta.',     2150.00, 15,  30.00, 1, NULL);
INSERT INTO Operativo.Productos (IdProducto, Nombre, Descripcion, Precio, Stock, MargenGanancia, Activo, FotoUrl) VALUES
(3, N'Mochila Vision Guard Kids',   N'Para niños escolares, estampado dual.',   1090.00, 40,  20.00, 1, NULL);
INSERT INTO Operativo.Productos (IdProducto, Nombre, Descripcion, Precio, Stock, MargenGanancia, Activo, FotoUrl) VALUES
(4, N'Mochila Vision Guard Ejecutiva', N'Acabados premium y panel solar.',      2450.00, 8,   35.00, 1, NULL);
INSERT INTO Operativo.Productos (IdProducto, Nombre, Descripcion, Precio, Stock, MargenGanancia, Activo, FotoUrl) VALUES
(5, N'Cangurera universal',         N'Accesorio de cintura multipropósito.',     400.00, 100, 40.00, 1, NULL);
INSERT INTO Operativo.Productos (IdProducto, Nombre, Descripcion, Precio, Stock, MargenGanancia, Activo, FotoUrl) VALUES
(6, N'Mochila Vision Guard Elite',  N'Edición especial con techo nuboso.',       2980.00, 5,   40.00, 1, NULL);
INSERT INTO Operativo.Productos (IdProducto, Nombre, Descripcion, Precio, Stock, MargenGanancia, Activo, FotoUrl) VALUES
(7, N'Mochila accesible Vision',    N'Mochila adaptada con control por voz.',    3850.00, 3,   50.00, 1, NULL);

SET IDENTITY_INSERT Operativo.Productos OFF;

-- ---------------------------------------------------------------------
-- 4. RECETA PRODUCTO - MATERIA PRIMA
-- ---------------------------------------------------------------------
INSERT INTO Operativo.ProductoMateriaPrima (IdProducto, IdMateriaPrima, Cantidad) VALUES
(1, 1, 40.00), (1, 3, 2.00), (1, 4, 10.00), (1, 10, 1.00);
INSERT INTO Operativo.ProductoMateriaPrima (IdProducto, IdMateriaPrima, Cantidad) VALUES
(2, 1, 50.00), (2, 3, 2.00), (2, 4, 12.00), (2, 6, 1.50), (2, 8, 1.00), (2, 10, 2.00);
INSERT INTO Operativo.ProductoMateriaPrima (IdProducto, IdMateriaPrima, Cantidad) VALUES
(3, 1, 30.00), (3, 3, 2.00), (3, 4, 8.00), (3, 10, 1.00);
INSERT INTO Operativo.ProductoMateriaPrima (IdProducto, IdMateriaPrima, Cantidad) VALUES
(4, 1, 60.00), (4, 3, 3.00), (4, 4, 15.00), (4, 6, 2.00), (4, 7, 1.00), (4, 10, 3.00);
INSERT INTO Operativo.ProductoMateriaPrima (IdProducto, IdMateriaPrima, Cantidad) VALUES
(5, 4, 5.00), (5, 3, 1.00), (5, 10, 0.50);
INSERT INTO Operativo.ProductoMateriaPrima (IdProducto, IdMateriaPrima, Cantidad) VALUES
(6, 1, 55.00), (6, 4, 14.00), (6, 6, 2.00), (6, 7, 1.00), (6, 9, 1.00);
INSERT INTO Operativo.ProductoMateriaPrima (IdProducto, IdMateriaPrima, Cantidad) VALUES
(7, 1, 70.00), (7, 4, 18.00), (7, 6, 2.00), (7, 7, 2.00), (7, 8, 1.00), (7, 9, 1.00);

-- ---------------------------------------------------------------------
-- 5. COMPRAS (historial para calcular el precio promedio)
-- ---------------------------------------------------------------------
SET IDENTITY_INSERT Operativo.Compras ON;

INSERT INTO Operativo.Compras (IdCompra, FechaCompra, IdProveedor, Total) VALUES
(1,  '2026-03-15T09:10:00.000', 1, 4340.00);
INSERT INTO Operativo.Compras (IdCompra, FechaCompra, IdProveedor, Total) VALUES
(2,  '2026-03-28T11:40:00.000', 2, 975.00);
INSERT INTO Operativo.Compras (IdCompra, FechaCompra, IdProveedor, Total) VALUES
(3,  '2026-04-12T10:05:00.000', 3, 19000.00);
INSERT INTO Operativo.Compras (IdCompra, FechaCompra, IdProveedor, Total) VALUES
(4,  '2026-04-25T16:20:00.000', 3, 12000.00);
INSERT INTO Operativo.Compras (IdCompra, FechaCompra, IdProveedor, Total) VALUES
(5,  '2026-05-06T08:45:00.000', 8, 2908.00);
INSERT INTO Operativo.Compras (IdCompra, FechaCompra, IdProveedor, Total) VALUES
(6,  '2026-05-18T13:30:00.000', 1, 2100.00);
INSERT INTO Operativo.Compras (IdCompra, FechaCompra, IdProveedor, Total) VALUES
(7,  '2026-05-29T15:10:00.000', 2, 1960.00);
INSERT INTO Operativo.Compras (IdCompra, FechaCompra, IdProveedor, Total) VALUES
(8,  '2026-06-10T10:55:00.000', 3, 4715.00);
INSERT INTO Operativo.Compras (IdCompra, FechaCompra, IdProveedor, Total) VALUES
(9,  '2026-06-22T09:15:00.000', 3, 14100.00);
INSERT INTO Operativo.Compras (IdCompra, FechaCompra, IdProveedor, Total) VALUES
(10, '2026-07-03T12:40:00.000', 8, 4550.00);
INSERT INTO Operativo.Compras (IdCompra, FechaCompra, IdProveedor, Total) VALUES
(11, '2026-07-15T08:30:00.000', 1, 3160.00);
INSERT INTO Operativo.Compras (IdCompra, FechaCompra, IdProveedor, Total) VALUES
(12, '2026-07-28T14:05:00.000', 2, 1960.00);

SET IDENTITY_INSERT Operativo.Compras OFF;

-- ---------------------------------------------------------------------
-- 6. DETALLE DE COMPRAS
-- ---------------------------------------------------------------------
SET IDENTITY_INSERT Operativo.DetalleCompra ON;

INSERT INTO Operativo.DetalleCompra (IdDetalleCompra, IdCompra, IdMateriaPrima, Cantidad, PrecioUnitario) VALUES
(1, 1, 1, 120, 14.50), (2, 1, 4, 200, 13.00);
INSERT INTO Operativo.DetalleCompra (IdDetalleCompra, IdCompra, IdMateriaPrima, Cantidad, PrecioUnitario) VALUES
(3, 2, 2, 300, 2.50), (4, 2, 10, 150, 1.50);
INSERT INTO Operativo.DetalleCompra (IdDetalleCompra, IdCompra, IdMateriaPrima, Cantidad, PrecioUnitario) VALUES
(5, 3, 6, 200, 95.00);
INSERT INTO Operativo.DetalleCompra (IdDetalleCompra, IdCompra, IdMateriaPrima, Cantidad, PrecioUnitario) VALUES
(6, 4, 5, 300, 8.00), (7, 4, 6, 100, 96.00);
INSERT INTO Operativo.DetalleCompra (IdDetalleCompra, IdCompra, IdMateriaPrima, Cantidad, PrecioUnitario) VALUES
(8, 5, 8, 60, 6.80), (9, 5, 4, 100, 25.00);
INSERT INTO Operativo.DetalleCompra (IdDetalleCompra, IdCompra, IdMateriaPrima, Cantidad, PrecioUnitario) VALUES
(10, 6, 3, 200, 3.00), (11, 6, 1, 100, 15.00);
INSERT INTO Operativo.DetalleCompra (IdDetalleCompra, IdCompra, IdMateriaPrima, Cantidad, PrecioUnitario) VALUES
(12, 7, 10, 300, 2.20), (13, 7, 2, 500, 2.60);
INSERT INTO Operativo.DetalleCompra (IdDetalleCompra, IdCompra, IdMateriaPrima, Cantidad, PrecioUnitario) VALUES
(14, 8, 5, 150, 8.50), (15, 8, 7, 80, 43.00);
INSERT INTO Operativo.DetalleCompra (IdDetalleCompra, IdCompra, IdMateriaPrima, Cantidad, PrecioUnitario) VALUES
(16, 9, 6, 100, 97.00), (17, 9, 7, 100, 44.00);
INSERT INTO Operativo.DetalleCompra (IdDetalleCompra, IdCompra, IdMateriaPrima, Cantidad, PrecioUnitario) VALUES
(18, 10, 4, 300, 6.50), (19, 10, 9, 100, 26.00);
INSERT INTO Operativo.DetalleCompra (IdDetalleCompra, IdCompra, IdMateriaPrima, Cantidad, PrecioUnitario) VALUES
(20, 11, 1, 120, 14.00), (21, 11, 4, 200, 7.40);
INSERT INTO Operativo.DetalleCompra (IdDetalleCompra, IdCompra, IdMateriaPrima, Cantidad, PrecioUnitario) VALUES
(22, 12, 2, 300, 2.70), (23, 12, 10, 200, 4.20), (24, 12, 3, 100, 3.10);

SET IDENTITY_INSERT Operativo.DetalleCompra OFF;

PRINT 'Dataset de prueba insertado correctamente.';