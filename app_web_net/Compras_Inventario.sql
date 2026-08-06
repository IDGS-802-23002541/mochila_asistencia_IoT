PRINT 'CANGURERA INTELIGENTE - Recreacion del modulo de Compras/Inventario (esquema Operativo)';
PRINT 'Ejecutar contra la base de datos real (db57112). No usa USE ni GO.';

IF NOT EXISTS (SELECT 1 FROM sys.schemas WHERE name = N'Operativo')
BEGIN
    EXEC(N'CREATE SCHEMA Operativo');
END;

-- =====================================================================
-- 0. ELIMINAR TABLAS EN ORDEN DE DEPENDENCIAS (hacia abajo)
-- =====================================================================
IF OBJECT_ID(N'Operativo.DetalleCompra', 'U') IS NOT NULL
    DROP TABLE Operativo.DetalleCompra;
IF OBJECT_ID(N'Operativo.DetalleVenta', 'U') IS NOT NULL
    DROP TABLE Operativo.DetalleVenta;
IF OBJECT_ID(N'Operativo.Compras', 'U') IS NOT NULL
    DROP TABLE Operativo.Compras;
IF OBJECT_ID(N'Operativo.Ventas', 'U') IS NOT NULL
    DROP TABLE Operativo.Ventas;
IF OBJECT_ID(N'Operativo.ProductoMateriaPrima', 'U') IS NOT NULL
    DROP TABLE Operativo.ProductoMateriaPrima;
IF OBJECT_ID(N'Operativo.MateriaPrima', 'U') IS NOT NULL
    DROP TABLE Operativo.MateriaPrima;
IF OBJECT_ID(N'Operativo.Productos', 'U') IS NOT NULL
    DROP TABLE Operativo.Productos;
IF OBJECT_ID(N'Operativo.Proveedores', 'U') IS NOT NULL
    DROP TABLE Operativo.Proveedores;

-- ============ 2. PROVEEDORES ============
CREATE TABLE Operativo.Proveedores (
    IdProveedor INT IDENTITY(1,1) PRIMARY KEY,
    Nombre      NVARCHAR(100) NOT NULL,
    Telefono    NVARCHAR(20)  NULL,
    Correo      NVARCHAR(100) NULL,
    Direccion   NVARCHAR(200) NULL,
    Activo      BIT           NOT NULL DEFAULT (1)
);

-- ============ 3. MATERIA PRIMA ============
CREATE TABLE Operativo.MateriaPrima (
    IdMateriaPrima INT IDENTITY(1,1) PRIMARY KEY,
    Nombre         NVARCHAR(100)          NOT NULL,
    Descripcion    NVARCHAR(MAX)          NULL,
    CostoUnitario  DECIMAL(18,2)          NOT NULL DEFAULT (0),
    Stock          INT                    NOT NULL DEFAULT (0),
    StockMinimo    INT                    NOT NULL DEFAULT (0),
    IdProveedor    INT                    NOT NULL
        FOREIGN KEY REFERENCES Operativo.Proveedores(IdProveedor)
);

IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = N'IX_MateriaPrima_IdProveedor' AND object_id = OBJECT_ID(N'Operativo.MateriaPrima'))
    CREATE INDEX IX_MateriaPrima_IdProveedor ON Operativo.MateriaPrima(IdProveedor);

-- ============ 4. PRODUCTOS ============
CREATE TABLE Operativo.Productos (
    IdProducto     INT IDENTITY(1,1) PRIMARY KEY,
    Nombre         NVARCHAR(100)   NOT NULL,
    Descripcion    NVARCHAR(MAX)   NULL,
    Precio         DECIMAL(18,2)   NOT NULL DEFAULT (0),
    Stock          INT             NOT NULL DEFAULT (0),
    MargenGanancia DECIMAL(5,2)    NOT NULL DEFAULT (20),
    Activo         BIT             NOT NULL DEFAULT (1),
    FotoUrl        NVARCHAR(500)   NULL
);

-- ============ 5. PRODUCTO - MATERIA PRIMA (recetas) ============
CREATE TABLE Operativo.ProductoMateriaPrima (
    IdProducto     INT            NOT NULL,
    IdMateriaPrima INT            NOT NULL,
    Cantidad       DECIMAL(18,2)  NOT NULL DEFAULT (0),
    PRIMARY KEY (IdProducto, IdMateriaPrima),
    FOREIGN KEY (IdProducto)     REFERENCES Operativo.Productos(IdProducto),
    FOREIGN KEY (IdMateriaPrima) REFERENCES Operativo.MateriaPrima(IdMateriaPrima)
);

-- ============ 6. COMPRAS (cabecera) ============
CREATE TABLE Operativo.Compras (
    IdCompra     INT IDENTITY(1,1) PRIMARY KEY,
    FechaCompra  DATETIME2(3)      NOT NULL DEFAULT SYSUTCDATETIME(),
    IdProveedor  INT               NOT NULL
        FOREIGN KEY REFERENCES Operativo.Proveedores(IdProveedor),
    Total        DECIMAL(18,2)     NOT NULL DEFAULT (0)
);

IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'IX_Compras_IdProveedor' AND object_id = OBJECT_ID(N'Operativo.Compras'))
    CREATE INDEX IX_Compras_IdProveedor ON Operativo.Compras(IdProveedor);

-- ============ 7. DETALLE DE COMPRA ============
CREATE TABLE Operativo.DetalleCompra (
    IdDetalleCompra INT IDENTITY(1,1) PRIMARY KEY,
    IdCompra        INT           NOT NULL
        FOREIGN KEY REFERENCES Operativo.Compras(IdCompra),
    IdMateriaPrima  INT           NOT NULL,
    Cantidad        INT           NOT NULL,
    PrecioUnitario  DECIMAL(18,2) NOT NULL DEFAULT (0),
    FOREIGN KEY (IdMateriaPrima) REFERENCES Operativo.MateriaPrima(IdMateriaPrima)
);

IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'IX_DetalleCompra_IdCompra' AND object_id = OBJECT_ID(N'Operativo.DetalleCompra'))
    CREATE INDEX IX_DetalleCompra_IdCompra ON Operativo.DetalleCompra(IdCompra);

-- ============ 7b. VENTAS / DETALLE VENTA (no tocar: no parte del modulo de compras) ============
-- IF OBJECT_ID(N'Operativo.Ventas','U') IS NOT NULL DROP TABLE Operativo.Ventas;
-- CREATE TABLE Operativo.Ventas (
--     IdVenta     INT IDENTITY(1,1) PRIMARY KEY,
--     FechaVenta  DATETIME2(3)    NOT NULL DEFAULT SYSUTCDATETIME(),
--     Total       DECIMAL(18,2)   NOT NULL DEFAULT (0)
-- );
-- IF OBJECT_ID(N'Operativo.DetalleVenta','U') IS NOT NULL DROP TABLE Operativo.DetalleVenta;
-- CREATE TABLE Operativo.DetalleVenta (
--     IdDetalleVenta INT IDENTITY(1,1) PRIMARY KEY,
--     IdVenta        INT NOT NULL REFERENCES Operativo.Ventas(IdVenta),
--     IdProducto     INT NOT NULL REFERENCES Operativo.Productos(IdProducto),
--     Cantidad       INT NOT NULL,
--     PrecioUnitario DECIMAL(18,2) NOT NULL DEFAULT (0)
-- );

-- ============ 8. PROCEDIMIENTO: Registrar compra y actualizar inventario ============
IF OBJECT_ID(N'Operativo.Sp_Registrar_Compra', 'P') IS NOT NULL
    EXEC(N'DROP PROCEDURE Operativo.Sp_Registrar_Compra');

EXEC(N'
CREATE PROCEDURE Operativo.Sp_Registrar_Compra
    @IdProveedor INT,
    @Total DECIMAL(18,2) = NULL
AS
BEGIN
    SET NOCOUNT ON;
    BEGIN TRY
        BEGIN TRAN;
        INSERT INTO Operativo.Compras (FechaCompra, IdProveedor, Total)
        VALUES (SYSUTCDATETIME(), @IdProveedor, ISNULL(@Total, 0));
        SELECT SCOPE_IDENTITY() AS IdCompra;
        COMMIT;
    END TRY
    BEGIN CATCH
        ROLLBACK;
        THROW;
    END CATCH
END');

PRINT N'Modulo de Compras de Materia Prima creado correctamente.';