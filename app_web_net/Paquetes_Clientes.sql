PRINT 'CANGURERA INTELIGENTE - Modulo paquetes cliente (esquema Operativo)';
PRINT 'Ejecutar contra la base de datos real (db57112). No usa USE ni GO.';

IF NOT EXISTS (SELECT 1 FROM sys.schemas WHERE name = N'Operativo')
BEGIN
    EXEC(N'CREATE SCHEMA Operativo');
END;

-- =====================================================================
-- 1. PRODUCTOS: un paquete incluye una mochila por defecto
-- =====================================================================
IF COL_LENGTH(N'Operativo.Productos', N'IncluyeMochila') IS NULL
BEGIN
    ALTER TABLE Operativo.Productos
        ADD IncluyeMochila BIT NOT NULL CONSTRAINT DF_Productos_IncluyeMochila DEFAULT (1);
    PRINT '  Productos.IncluyeMochila agregado.';
END
ELSE
    PRINT '  Productos.IncluyeMochila ya existe.';

-- =====================================================================
-- 2. PRODUCTO CONTENIDO (extras del paquete)
--    Un paquete (IdProducto) puede incluir otros productos (IdItem)
-- =====================================================================
IF OBJECT_ID(N'Operativo.ProductoContenido', 'U') IS NULL
BEGIN
    CREATE TABLE Operativo.ProductoContenido (
        IdProductoContenido INT IDENTITY(1,1) PRIMARY KEY,
        IdProducto          INT      NOT NULL,
        IdItem              INT      NOT NULL,
        Cantidad            INT      NOT NULL DEFAULT (1),
        CONSTRAINT FK_ProductoContenido_Producto
            FOREIGN KEY (IdProducto) REFERENCES Operativo.Productos(IdProducto),
        CONSTRAINT FK_ProductoContenido_Item
            FOREIGN KEY (IdItem) REFERENCES Operativo.Productos(IdProducto),
        CONSTRAINT UQ_ProductoContenido_Paquete_Item UNIQUE (IdProducto, IdItem)
    );

    CREATE INDEX IX_ProductoContenido_IdProducto ON Operativo.ProductoContenido(IdProducto);
    PRINT '  Tabla Operativo.ProductoContenido creada.';
END
ELSE
    PRINT '  Tabla Operativo.ProductoContenido ya existe.';

-- =====================================================================
-- 3. PRODUCTO DOCUMENTO (guias y manuales, varios archivos en base64)
-- =====================================================================
IF OBJECT_ID(N'Operativo.ProductoDocumento', 'U') IS NULL
BEGIN
    CREATE TABLE Operativo.ProductoDocumento (
        IdProductoDocumento INT IDENTITY(1,1) PRIMARY KEY,
        IdProducto          INT            NOT NULL,
        NombreArchivo       NVARCHAR(255)  NOT NULL,
        TipoContenido       NVARCHAR(100)  NOT NULL,
        Descripcion         NVARCHAR(255)  NULL,
        ContenidoBase64     NVARCHAR(MAX)  NOT NULL,
        FechaSubida         DATETIME2(3)   NOT NULL DEFAULT SYSUTCDATETIME(),
        CONSTRAINT FK_ProductoDocumento_Producto
            FOREIGN KEY (IdProducto) REFERENCES Operativo.Productos(IdProducto)
    );

    CREATE INDEX IX_ProductoDocumento_IdProducto ON Operativo.ProductoDocumento(IdProducto);
    PRINT '  Tabla Operativo.ProductoDocumento creada.';
END
ELSE
    PRINT '  Tabla Operativo.ProductoDocumento ya existe.';

-- =====================================================================
-- 4. VENTAS ligadas a la organizacion compradora
-- =====================================================================
IF OBJECT_ID(N'Operativo.Ventas', 'U') IS NULL
BEGIN
    CREATE TABLE Operativo.Ventas (
        IdVenta      INT IDENTITY(1,1) PRIMARY KEY,
        IdOrganizacion INT           NOT NULL,
        FechaVenta   DATETIME2(3)    NOT NULL DEFAULT SYSUTCDATETIME(),
        Total        DECIMAL(18,2)   NOT NULL DEFAULT (0),
        CONSTRAINT FK_Ventas_Organizacion
            FOREIGN KEY (IdOrganizacion) REFERENCES Operativo.Organizaciones(Id)
    );
    PRINT '  Tabla Operativo.Ventas creada.';
END
ELSE IF COL_LENGTH(N'Operativo.Ventas', N'IdOrganizacion') IS NULL
BEGIN
    ALTER TABLE Operativo.Ventas
        ADD IdOrganizacion INT NOT NULL
            CONSTRAINT DF_Ventas_IdOrganizacion DEFAULT (0);
    ALTER TABLE Operativo.Ventas
        ADD CONSTRAINT FK_Ventas_Organizacion
            FOREIGN KEY (IdOrganizacion) REFERENCES Operativo.Organizaciones(Id);
    PRINT '  Operativo.Ventas.IdOrganizacion agregado.';
END
ELSE
    PRINT '  Operativo.Ventas ya existe con IdOrganizacion.';

IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = N'IX_Ventas_IdOrganizacion' AND object_id = OBJECT_ID(N'Operativo.Ventas'))
    CREATE INDEX IX_Ventas_IdOrganizacion ON Operativo.Ventas(IdOrganizacion);

-- =====================================================================
-- 5. DETALLE DE VENTA (asegurar existencia)
-- =====================================================================
IF OBJECT_ID(N'Operativo.DetalleVenta', 'U') IS NULL
BEGIN
    CREATE TABLE Operativo.DetalleVenta (
        IdDetalleVenta INT IDENTITY(1,1) PRIMARY KEY,
        IdVenta        INT           NOT NULL,
        IdProducto     INT           NOT NULL,
        Cantidad       INT           NOT NULL,
        PrecioUnitario DECIMAL(18,2) NOT NULL DEFAULT (0),
        CONSTRAINT FK_DetalleVenta_Venta
            FOREIGN KEY (IdVenta) REFERENCES Operativo.Ventas(IdVenta),
        CONSTRAINT FK_DetalleVenta_Producto
            FOREIGN KEY (IdProducto) REFERENCES Operativo.Productos(IdProducto)
    );

    CREATE INDEX IX_DetalleVenta_IdVenta ON Operativo.DetalleVenta(IdVenta);
    PRINT '  Tabla Operativo.DetalleVenta creada.';
END
ELSE
    PRINT '  Tabla Operativo.DetalleVenta ya existe.';

PRINT N'Modulo de paquetes cliente creado correctamente.';