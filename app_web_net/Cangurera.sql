-- =====================================================================
-- CANGURERA INTELIGENTE - Modelo de Base de Datos v4.2 (FINAL)
-- SQL Server | Esquema OLTP + OLAP (Cumplimiento académico)
-- =====================================================================

USE master;
GO

IF NOT EXISTS (SELECT * FROM sys.databases WHERE name = 'CangureraInteligenteDB')
    CREATE DATABASE CangureraInteligenteDB;
GO

USE CangureraInteligenteDB;
GO

-- Limpieza de esquemas previos
IF EXISTS (SELECT * FROM sys.schemas WHERE name = 'Analitico') 
BEGIN
    DROP PROCEDURE IF EXISTS Analitico.Sp_Cargar_DW;
    DROP TABLE IF EXISTS Analitico.Hechos_Eventos;
    DROP SCHEMA Analitico;
END
GO

IF EXISTS (SELECT * FROM sys.schemas WHERE name = 'Operativo')
BEGIN
    DROP TABLE IF EXISTS Operativo.Eventos_Detectados;
    DROP TABLE IF EXISTS Operativo.Recorridos;
    DROP TABLE IF EXISTS Operativo.Cat_TiposDiscapacidad;
    DROP TABLE IF EXISTS Operativo.Cat_TiposEvento;
    DROP TABLE IF EXISTS Operativo.Dispositivos;
    DROP TABLE IF EXISTS Operativo.Organizaciones;
    DROP SCHEMA Operativo;
END
GO

CREATE SCHEMA Operativo;
GO
CREATE SCHEMA Analitico;
GO

-- =====================================================================
-- 1. ESQUEMA OPERATIVO (OLTP)
-- =====================================================================

CREATE TABLE Operativo.Organizaciones (
    Id                 INT IDENTITY(1,1) PRIMARY KEY,
    Nombre             NVARCHAR(150) NOT NULL,
    Sector             NVARCHAR(50)  NOT NULL,
    Contacto_Principal NVARCHAR(100) NULL,
    Email_Contacto     VARCHAR(100)  NULL,
    Contrasena_Hash    VARCHAR(255)  NULL,
    Rol                VARCHAR(20)   NOT NULL DEFAULT 'usuario'
        CONSTRAINT chk_organizaciones_rol CHECK (Rol IN ('usuario', 'admin')),
    Es_Interna         BIT           NOT NULL DEFAULT 0,
    FechaCreacion      DATETIME2(3)  NOT NULL DEFAULT SYSUTCDATETIME(),
    Estado_Activo      BIT           NOT NULL DEFAULT 1
);

CREATE TABLE Operativo.Dispositivos (
    Id               INT IDENTITY(1,1) PRIMARY KEY,
    OrganizacionId   INT          NOT NULL FOREIGN KEY REFERENCES Operativo.Organizaciones(Id),
    MacAddress       VARCHAR(17)  NOT NULL UNIQUE,
    FechaRegistro    DATETIME2(3) NOT NULL DEFAULT SYSUTCDATETIME(),
    UltimaConexion   DATETIME2(3) NULL,
    Estado           VARCHAR(20)  NOT NULL DEFAULT 'Activo'
);

CREATE TABLE Operativo.Cat_TiposEvento (
    Id           INT IDENTITY(1,1) PRIMARY KEY,
    NombreEvento VARCHAR(50)  NOT NULL UNIQUE,
    Severidad    VARCHAR(20)  NOT NULL
);

CREATE TABLE Operativo.Cat_TiposDiscapacidad (
    Id           INT IDENTITY(1,1) PRIMARY KEY,
    Nombre       NVARCHAR(50) NOT NULL UNIQUE
);

CREATE TABLE Operativo.Recorridos (
    Id                   INT IDENTITY(1,1) PRIMARY KEY,
    DispositivoId        INT          NOT NULL FOREIGN KEY REFERENCES Operativo.Dispositivos(Id),
    FechaInicio          DATETIME2(3) NOT NULL DEFAULT SYSUTCDATETIME(),
    FechaFin             DATETIME2(3) NULL,
    Usuario_Edad         INT          NULL,
    DiscapacidadId       INT          NULL FOREIGN KEY REFERENCES Operativo.Cat_TiposDiscapacidad(Id),
    Ruta_Coordenadas     VARCHAR(MAX) NOT NULL
        CONSTRAINT chk_ruta_json CHECK (ISJSON(Ruta_Coordenadas) = 1)
);

CREATE TABLE Operativo.Eventos_Detectados (
    Id              BIGINT IDENTITY(1,1) PRIMARY KEY,
    RecorridoId     INT           NOT NULL FOREIGN KEY REFERENCES Operativo.Recorridos(Id),
    TipoEventoId    INT           NOT NULL FOREIGN KEY REFERENCES Operativo.Cat_TiposEvento(Id),
    TimestampEvento DATETIME2(3)  NOT NULL DEFAULT SYSUTCDATETIME(),
    Latitud         DECIMAL(10,8) NULL,
    Longitud        DECIMAL(10,8) NULL,
    Geo_Es_Estimado BIT           NOT NULL DEFAULT 0,
    FuerzaImpactoG  DECIMAL(5,2)  NULL
);

-- Índices de Rendimiento
CREATE INDEX IX_Eventos_RecorridoId ON Operativo.Eventos_Detectados(RecorridoId);
CREATE INDEX IX_Eventos_Timestamp   ON Operativo.Eventos_Detectados(TimestampEvento);
CREATE INDEX IX_Dispositivos_OrganizacionId ON Operativo.Dispositivos(OrganizacionId);
CREATE INDEX IX_Recorridos_DispositivoId ON Operativo.Recorridos(DispositivoId);
CREATE UNIQUE INDEX UX_Organizaciones_Email_Contacto
    ON Operativo.Organizaciones(Email_Contacto)
    WHERE Email_Contacto IS NOT NULL;
GO

-- =====================================================================
-- 2. ESQUEMA ANALÍTICO (Simplificado para cumplimiento académico)
-- =====================================================================

CREATE TABLE Analitico.Hechos_Eventos (
    Id_Hecho        BIGINT PRIMARY KEY,
    Fecha           DATETIME2(3),
    Organizacion    NVARCHAR(150),
    TipoEvento      VARCHAR(50),
    Discapacidad    NVARCHAR(50),
    Latitud         DECIMAL(10,8) NULL,
    Longitud        DECIMAL(11,8) NULL,
    Geo_Es_Estimado BIT,
    FuerzaImpactoG  DECIMAL(5,2)
);
GO

-- Procedimiento de volcado simple con LEFT JOIN para evitar pérdida de datos
CREATE PROCEDURE Analitico.Sp_Cargar_DW AS
BEGIN
    SET NOCOUNT ON;

    TRUNCATE TABLE Analitico.Hechos_Eventos;

    INSERT INTO Analitico.Hechos_Eventos
        (Id_Hecho, Fecha, Organizacion, TipoEvento, Discapacidad,
         Latitud, Longitud, Geo_Es_Estimado, FuerzaImpactoG)
    SELECT
        e.Id,
        e.TimestampEvento,
        o.Nombre,
        t.NombreEvento,
        ISNULL(d.Nombre, N'No especificado'),
        e.Latitud,
        e.Longitud,
        e.Geo_Es_Estimado,
        e.FuerzaImpactoG
    FROM Operativo.Eventos_Detectados e
    JOIN Operativo.Recorridos r ON e.RecorridoId = r.Id
    JOIN Operativo.Cat_TiposEvento t ON e.TipoEventoId = t.Id
    LEFT JOIN Operativo.Cat_TiposDiscapacidad d ON r.DiscapacidadId = d.Id
    JOIN Operativo.Dispositivos disp ON r.DispositivoId = disp.Id
    JOIN Operativo.Organizaciones o ON disp.OrganizacionId = o.Id;
END;
GO

