-- Mock v6 -- puntos reales de riesgo, dispositivo unico Id 10
-- Rango simulado: 1-15 julio 2026. Insercion ADITIVA, no borra nada.

-- Recorrido mock v6 #1 (DispositivoId 10)
DECLARE @NewId TABLE (Id BIGINT);
INSERT INTO Operativo.Recorridos (DispositivoId, FechaInicio, FechaFin, Ruta_Coordenadas)
OUTPUT INSERTED.Id INTO @NewId
VALUES (10, '2026-07-01 16:57:00', '2026-07-01 17:10:30', NULL);

DECLARE @RecId BIGINT = (SELECT TOP 1 Id FROM @NewId);

INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-01 16:57:00', 21.063941, -101.581781);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-01 16:57:30', 21.063906, -101.581787);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-01 16:58:00', 21.063871, -101.581775);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-01 16:58:30', 21.063821, -101.581752);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-01 16:59:00', 21.063803, -101.581535);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-01 16:59:30', 21.063724, -101.581517);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-01 17:00:00', 21.063548, -101.580892);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-01 17:00:30', 21.063495, -101.580708);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-01 17:01:00', 21.063465, -101.58062);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-01 17:01:30', 21.063416, -101.580351);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-01 17:02:00', 21.063205, -101.579621);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-01 17:02:30', 21.063073, -101.57897);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-01 17:03:00', 21.062987, -101.57879);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-01 17:03:30', 21.06292, -101.578814);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-01 17:04:00', 21.062917, -101.578798);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-01 17:04:30', 21.062895, -101.57878);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-01 17:05:00', 21.06287, -101.578685);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-01 17:05:30', 21.062802, -101.578722);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-01 17:06:00', 21.062845, -101.578806);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-01 17:06:30', 21.062656, -101.578868);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-01 17:07:00', 21.062642, -101.578744);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-01 17:07:30', 21.062551, -101.578776);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-01 17:08:00', 21.062826, -101.579741);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-01 17:08:30', 21.06297, -101.580218);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-01 17:09:00', 21.063106, -101.580747);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-01 17:09:30', 21.063114, -101.580858);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-01 17:10:00', 21.063234, -101.58119);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-01 17:10:30', 21.063031, -101.581236);

INSERT INTO Operativo.Eventos_Detectados (RecorridoId, TipoEventoId, TimestampEvento, Latitud, Longitud, Geo_Es_Estimado) VALUES (@RecId, 2, '2026-07-01 16:59:08', 21.063632, -101.581295, 0);
INSERT INTO Operativo.Eventos_Detectados (RecorridoId, TipoEventoId, TimestampEvento, Latitud, Longitud, Geo_Es_Estimado) VALUES (@RecId, 2, '2026-07-01 17:05:17', 21.063568, -101.581246, 0);
GO

-- Recorrido mock v6 #2 (DispositivoId 10)
DECLARE @NewId TABLE (Id BIGINT);
INSERT INTO Operativo.Recorridos (DispositivoId, FechaInicio, FechaFin, Ruta_Coordenadas)
OUTPUT INSERTED.Id INTO @NewId
VALUES (10, '2026-07-02 19:36:00', '2026-07-02 19:49:30', NULL);

DECLARE @RecId BIGINT = (SELECT TOP 1 Id FROM @NewId);

INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-02 19:36:00', 21.063974, -101.581777);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-02 19:36:30', 21.063877, -101.581794);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-02 19:37:00', 21.063884, -101.581764);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-02 19:37:30', 21.063822, -101.581772);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-02 19:38:00', 21.063823, -101.581512);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-02 19:38:30', 21.063714, -101.581528);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-02 19:39:00', 21.063535, -101.580876);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-02 19:39:30', 21.063506, -101.580697);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-02 19:40:00', 21.063494, -101.580636);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-02 19:40:30', 21.063398, -101.580341);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-02 19:41:00', 21.063205, -101.579642);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-02 19:41:30', 21.063054, -101.578972);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-02 19:42:00', 21.062993, -101.578771);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-02 19:42:30', 21.06294, -101.578801);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-02 19:43:00', 21.062908, -101.578817);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-02 19:43:30', 21.062899, -101.578784);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-02 19:44:00', 21.062881, -101.578663);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-02 19:44:30', 21.062817, -101.578716);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-02 19:45:00', 21.062847, -101.578796);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-02 19:45:30', 21.062659, -101.578839);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-02 19:46:00', 21.062633, -101.578746);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-02 19:46:30', 21.06256, -101.57875);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-02 19:47:00', 21.062835, -101.579763);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-02 19:47:30', 21.062963, -101.580206);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-02 19:48:00', 21.063091, -101.580753);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-02 19:48:30', 21.063122, -101.580845);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-02 19:49:00', 21.063219, -101.581191);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-02 19:49:30', 21.063025, -101.581224);

INSERT INTO Operativo.Eventos_Detectados (RecorridoId, TipoEventoId, TimestampEvento, Latitud, Longitud, Geo_Es_Estimado) VALUES (@RecId, 2, '2026-07-02 19:44:04', 21.063561, -101.581298, 0);
INSERT INTO Operativo.Eventos_Detectados (RecorridoId, TipoEventoId, TimestampEvento, Latitud, Longitud, Geo_Es_Estimado) VALUES (@RecId, 2, '2026-07-02 19:46:07', 21.063561, -101.5813, 0);
GO

-- Recorrido mock v6 #3 (DispositivoId 10)
DECLARE @NewId TABLE (Id BIGINT);
INSERT INTO Operativo.Recorridos (DispositivoId, FechaInicio, FechaFin, Ruta_Coordenadas)
OUTPUT INSERTED.Id INTO @NewId
VALUES (10, '2026-07-03 20:39:00', '2026-07-03 20:52:30', NULL);

DECLARE @RecId BIGINT = (SELECT TOP 1 Id FROM @NewId);

INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-03 20:39:00', 21.063945, -101.581793);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-03 20:39:30', 21.06389, -101.581773);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-03 20:40:00', 21.063876, -101.58179);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-03 20:40:30', 21.063796, -101.581751);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-03 20:41:00', 21.063809, -101.581527);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-03 20:41:30', 21.063731, -101.581515);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-03 20:42:00', 21.063551, -101.580873);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-03 20:42:30', 21.063503, -101.580731);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-03 20:43:00', 21.063481, -101.580623);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-03 20:43:30', 21.063401, -101.580322);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-03 20:44:00', 21.063231, -101.57964);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-03 20:44:30', 21.063065, -101.578961);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-03 20:45:00', 21.06299, -101.578806);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-03 20:45:30', 21.062954, -101.578804);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-03 20:46:00', 21.062928, -101.578783);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-03 20:46:30', 21.062915, -101.578752);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-03 20:47:00', 21.062877, -101.578671);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-03 20:47:30', 21.062808, -101.578686);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-03 20:48:00', 21.062846, -101.578824);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-03 20:48:30', 21.062635, -101.578866);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-03 20:49:00', 21.062641, -101.578761);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-03 20:49:30', 21.062571, -101.578777);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-03 20:50:00', 21.062817, -101.579754);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-03 20:50:30', 21.062947, -101.580212);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-03 20:51:00', 21.063096, -101.580738);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-03 20:51:30', 21.063129, -101.580845);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-03 20:52:00', 21.063233, -101.581184);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-03 20:52:30', 21.063038, -101.581253);

INSERT INTO Operativo.Eventos_Detectados (RecorridoId, TipoEventoId, TimestampEvento, Latitud, Longitud, Geo_Es_Estimado) VALUES (@RecId, 2, '2026-07-03 20:51:42', 21.06358, -101.581261, 0);
INSERT INTO Operativo.Eventos_Detectados (RecorridoId, TipoEventoId, TimestampEvento, Latitud, Longitud, Geo_Es_Estimado) VALUES (@RecId, 2, '2026-07-03 20:49:58', 21.063559, -101.581239, 0);
INSERT INTO Operativo.Eventos_Detectados (RecorridoId, TipoEventoId, TimestampEvento, Latitud, Longitud, Geo_Es_Estimado) VALUES (@RecId, 2, '2026-07-03 20:50:55', 21.063592, -101.581304, 0);
GO

-- Recorrido mock v6 #4 (DispositivoId 10)
DECLARE @NewId TABLE (Id BIGINT);
INSERT INTO Operativo.Recorridos (DispositivoId, FechaInicio, FechaFin, Ruta_Coordenadas)
OUTPUT INSERTED.Id INTO @NewId
VALUES (10, '2026-07-04 16:52:00', '2026-07-04 16:55:30', NULL);

DECLARE @RecId BIGINT = (SELECT TOP 1 Id FROM @NewId);

INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-04 16:52:00', 21.061741, -101.57841);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-04 16:52:30', 21.061796, -101.57842);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-04 16:53:00', 21.061848, -101.578387);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-04 16:53:30', 21.062039, -101.578315);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-04 16:54:00', 21.062203, -101.578278);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-04 16:54:30', 21.062353, -101.578219);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-04 16:55:00', 21.062453, -101.578653);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-04 16:55:30', 21.062151, -101.578636);

INSERT INTO Operativo.Eventos_Detectados (RecorridoId, TipoEventoId, TimestampEvento, Latitud, Longitud, Geo_Es_Estimado) VALUES (@RecId, 5, '2026-07-04 16:54:34', 21.06232, -101.578187, 0);
INSERT INTO Operativo.Eventos_Detectados (RecorridoId, TipoEventoId, TimestampEvento, Latitud, Longitud, Geo_Es_Estimado) VALUES (@RecId, 5, '2026-07-04 16:55:30', 21.062308, -101.578219, 0);
GO

-- Recorrido mock v6 #5 (DispositivoId 10)
DECLARE @NewId TABLE (Id BIGINT);
INSERT INTO Operativo.Recorridos (DispositivoId, FechaInicio, FechaFin, Ruta_Coordenadas)
OUTPUT INSERTED.Id INTO @NewId
VALUES (10, '2026-07-05 17:03:00', '2026-07-05 17:06:30', NULL);

DECLARE @RecId BIGINT = (SELECT TOP 1 Id FROM @NewId);

INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-05 17:03:00', 21.061757, -101.578385);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-05 17:03:30', 21.061812, -101.578388);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-05 17:04:00', 21.061875, -101.578366);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-05 17:04:30', 21.062003, -101.578328);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-05 17:05:00', 21.06221, -101.578261);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-05 17:05:30', 21.062368, -101.578225);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-05 17:06:00', 21.062465, -101.578647);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-05 17:06:30', 21.062164, -101.57865);

INSERT INTO Operativo.Eventos_Detectados (RecorridoId, TipoEventoId, TimestampEvento, Latitud, Longitud, Geo_Es_Estimado) VALUES (@RecId, 5, '2026-07-05 17:05:33', 21.062289, -101.578194, 0);
INSERT INTO Operativo.Eventos_Detectados (RecorridoId, TipoEventoId, TimestampEvento, Latitud, Longitud, Geo_Es_Estimado) VALUES (@RecId, 5, '2026-07-05 17:04:39', 21.062301, -101.578216, 0);
INSERT INTO Operativo.Eventos_Detectados (RecorridoId, TipoEventoId, TimestampEvento, Latitud, Longitud, Geo_Es_Estimado) VALUES (@RecId, 5, '2026-07-05 17:04:42', 21.06231, -101.578215, 0);
GO

-- Recorrido mock v6 #6 (DispositivoId 10)
DECLARE @NewId TABLE (Id BIGINT);
INSERT INTO Operativo.Recorridos (DispositivoId, FechaInicio, FechaFin, Ruta_Coordenadas)
OUTPUT INSERTED.Id INTO @NewId
VALUES (10, '2026-07-06 16:51:00', '2026-07-06 16:54:30', NULL);

DECLARE @RecId BIGINT = (SELECT TOP 1 Id FROM @NewId);

INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-06 16:51:00', 21.061764, -101.578382);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-06 16:51:30', 21.061799, -101.578416);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-06 16:52:00', 21.061845, -101.578376);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-06 16:52:30', 21.062021, -101.578317);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-06 16:53:00', 21.062187, -101.578256);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-06 16:53:30', 21.062343, -101.578198);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-06 16:54:00', 21.062475, -101.57864);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-06 16:54:30', 21.062164, -101.578646);

INSERT INTO Operativo.Eventos_Detectados (RecorridoId, TipoEventoId, TimestampEvento, Latitud, Longitud, Geo_Es_Estimado) VALUES (@RecId, 5, '2026-07-06 16:53:20', 21.062309, -101.578159, 0);
INSERT INTO Operativo.Eventos_Detectados (RecorridoId, TipoEventoId, TimestampEvento, Latitud, Longitud, Geo_Es_Estimado) VALUES (@RecId, 5, '2026-07-06 16:53:07', 21.062319, -101.578202, 0);
INSERT INTO Operativo.Eventos_Detectados (RecorridoId, TipoEventoId, TimestampEvento, Latitud, Longitud, Geo_Es_Estimado) VALUES (@RecId, 5, '2026-07-06 16:52:02', 21.062375, -101.578158, 0);
GO

-- Recorrido mock v6 #7 (DispositivoId 10)
DECLARE @NewId TABLE (Id BIGINT);
INSERT INTO Operativo.Recorridos (DispositivoId, FechaInicio, FechaFin, Ruta_Coordenadas)
OUTPUT INSERTED.Id INTO @NewId
VALUES (10, '2026-07-07 18:05:00', '2026-07-07 18:07:00', NULL);

DECLARE @RecId BIGINT = (SELECT TOP 1 Id FROM @NewId);

INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-07 18:05:00', 21.062666, -101.580301);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-07 18:05:30', 21.062959, -101.580232);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-07 18:06:00', 21.063094, -101.580759);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-07 18:06:30', 21.063026, -101.580759);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-07 18:07:00', 21.06281, -101.580737);

INSERT INTO Operativo.Eventos_Detectados (RecorridoId, TipoEventoId, TimestampEvento, Latitud, Longitud, Geo_Es_Estimado) VALUES (@RecId, 5, '2026-07-07 18:06:52', 21.062959, -101.580509, 0);
INSERT INTO Operativo.Eventos_Detectados (RecorridoId, TipoEventoId, TimestampEvento, Latitud, Longitud, Geo_Es_Estimado) VALUES (@RecId, 5, '2026-07-07 18:05:00', 21.062981, -101.580451, 0);
GO

-- Recorrido mock v6 #8 (DispositivoId 10)
DECLARE @NewId TABLE (Id BIGINT);
INSERT INTO Operativo.Recorridos (DispositivoId, FechaInicio, FechaFin, Ruta_Coordenadas)
OUTPUT INSERTED.Id INTO @NewId
VALUES (10, '2026-07-08 16:16:00', '2026-07-08 16:18:00', NULL);

DECLARE @RecId BIGINT = (SELECT TOP 1 Id FROM @NewId);

INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-08 16:16:00', 21.062663, -101.580268);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-08 16:16:30', 21.062938, -101.580207);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-08 16:17:00', 21.063076, -101.580764);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-08 16:17:30', 21.063064, -101.580771);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-08 16:18:00', 21.062834, -101.580736);

INSERT INTO Operativo.Eventos_Detectados (RecorridoId, TipoEventoId, TimestampEvento, Latitud, Longitud, Geo_Es_Estimado) VALUES (@RecId, 5, '2026-07-08 16:18:00', 21.062953, -101.580529, 0);
INSERT INTO Operativo.Eventos_Detectados (RecorridoId, TipoEventoId, TimestampEvento, Latitud, Longitud, Geo_Es_Estimado) VALUES (@RecId, 5, '2026-07-08 16:17:27', 21.062984, -101.580514, 0);
INSERT INTO Operativo.Eventos_Detectados (RecorridoId, TipoEventoId, TimestampEvento, Latitud, Longitud, Geo_Es_Estimado) VALUES (@RecId, 5, '2026-07-08 16:16:23', 21.063001, -101.580471, 0);
GO

-- Recorrido mock v6 #9 (DispositivoId 10)
DECLARE @NewId TABLE (Id BIGINT);
INSERT INTO Operativo.Recorridos (DispositivoId, FechaInicio, FechaFin, Ruta_Coordenadas)
OUTPUT INSERTED.Id INTO @NewId
VALUES (10, '2026-07-09 17:11:00', '2026-07-09 17:13:00', NULL);

DECLARE @RecId BIGINT = (SELECT TOP 1 Id FROM @NewId);

INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-09 17:11:00', 21.062672, -101.580292);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-09 17:11:30', 21.062939, -101.5802);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-09 17:12:00', 21.063073, -101.580754);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-09 17:12:30', 21.06306, -101.580776);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-09 17:13:00', 21.062831, -101.58073);

INSERT INTO Operativo.Eventos_Detectados (RecorridoId, TipoEventoId, TimestampEvento, Latitud, Longitud, Geo_Es_Estimado) VALUES (@RecId, 5, '2026-07-09 17:12:58', 21.062987, -101.580482, 0);
INSERT INTO Operativo.Eventos_Detectados (RecorridoId, TipoEventoId, TimestampEvento, Latitud, Longitud, Geo_Es_Estimado) VALUES (@RecId, 5, '2026-07-09 17:11:19', 21.063002, -101.580496, 0);
GO

-- Recorrido mock v6 #10 (DispositivoId 10)
DECLARE @NewId TABLE (Id BIGINT);
INSERT INTO Operativo.Recorridos (DispositivoId, FechaInicio, FechaFin, Ruta_Coordenadas)
OUTPUT INSERTED.Id INTO @NewId
VALUES (10, '2026-07-10 20:20:00', '2026-07-10 20:38:00', NULL);

DECLARE @RecId BIGINT = (SELECT TOP 1 Id FROM @NewId);

INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-10 20:20:00', 21.062716, -101.58173);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-10 20:20:30', 21.062759, -101.581763);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-10 20:21:00', 21.062804, -101.581725);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-10 20:21:30', 21.062841, -101.581741);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-10 20:22:00', 21.062881, -101.58173);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-10 20:22:30', 21.062946, -101.581706);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-10 20:23:00', 21.062979, -101.581633);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-10 20:23:30', 21.063097, -101.581626);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-10 20:24:00', 21.063126, -101.581643);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-10 20:24:30', 21.063185, -101.58164);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-10 20:25:00', 21.063216, -101.58163);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-10 20:25:30', 21.063227, -101.581615);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-10 20:26:00', 21.063311, -101.581585);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-10 20:26:30', 21.063361, -101.581598);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-10 20:27:00', 21.063333, -101.58156);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-10 20:27:30', 21.063359, -101.581491);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-10 20:28:00', 21.063321, -101.581392);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-10 20:28:30', 21.063294, -101.581304);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-10 20:29:00', 21.063271, -101.581202);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-10 20:29:30', 21.063249, -101.581054);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-10 20:30:00', 21.063186, -101.580904);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-10 20:30:30', 21.063164, -101.580787);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-10 20:31:00', 21.063126, -101.580598);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-10 20:31:30', 21.063101, -101.580503);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-10 20:32:00', 21.063069, -101.580389);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-10 20:32:30', 21.063023, -101.580262);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-10 20:33:00', 21.06298, -101.580138);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-10 20:33:30', 21.06295, -101.58002);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-10 20:34:00', 21.062895, -101.579894);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-10 20:34:30', 21.062894, -101.579801);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-10 20:35:00', 21.062854, -101.579746);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-10 20:35:30', 21.062808, -101.579744);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-10 20:36:00', 21.06294, -101.58023);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-10 20:36:30', 21.063091, -101.580767);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-10 20:37:00', 21.063128, -101.580849);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-10 20:37:30', 21.06323, -101.581205);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-10 20:38:00', 21.063025, -101.581242);

INSERT INTO Operativo.Eventos_Detectados (RecorridoId, TipoEventoId, TimestampEvento, Latitud, Longitud, Geo_Es_Estimado) VALUES (@RecId, 5, '2026-07-10 20:23:19', 21.06329, -101.581611, 0);
INSERT INTO Operativo.Eventos_Detectados (RecorridoId, TipoEventoId, TimestampEvento, Latitud, Longitud, Geo_Es_Estimado) VALUES (@RecId, 4, '2026-07-10 20:33:34', 21.062949, -101.581555, 0);
INSERT INTO Operativo.Eventos_Detectados (RecorridoId, TipoEventoId, TimestampEvento, Latitud, Longitud, Geo_Es_Estimado) VALUES (@RecId, 5, '2026-07-10 20:34:31', 21.063287, -101.581578, 0);
GO

-- Recorrido mock v6 #11 (DispositivoId 10)
DECLARE @NewId TABLE (Id BIGINT);
INSERT INTO Operativo.Recorridos (DispositivoId, FechaInicio, FechaFin, Ruta_Coordenadas)
OUTPUT INSERTED.Id INTO @NewId
VALUES (10, '2026-07-11 18:08:00', '2026-07-11 18:26:00', NULL);

DECLARE @RecId BIGINT = (SELECT TOP 1 Id FROM @NewId);

INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-11 18:08:00', 21.062712, -101.581725);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-11 18:08:30', 21.062773, -101.581752);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-11 18:09:00', 21.062791, -101.581735);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-11 18:09:30', 21.062822, -101.581727);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-11 18:10:00', 21.062885, -101.581711);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-11 18:10:30', 21.06294, -101.581732);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-11 18:11:00', 21.062943, -101.581603);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-11 18:11:30', 21.063091, -101.581648);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-11 18:12:00', 21.06315, -101.581615);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-11 18:12:30', 21.063184, -101.581633);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-11 18:13:00', 21.063195, -101.581655);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-11 18:13:30', 21.063243, -101.581644);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-11 18:14:00', 21.06328, -101.581614);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-11 18:14:30', 21.063337, -101.581581);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-11 18:15:00', 21.063351, -101.581531);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-11 18:15:30', 21.063342, -101.581477);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-11 18:16:00', 21.063326, -101.581402);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-11 18:16:30', 21.063299, -101.581315);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-11 18:17:00', 21.063294, -101.581165);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-11 18:17:30', 21.06326, -101.58106);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-11 18:18:00', 21.063193, -101.580904);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-11 18:18:30', 21.063159, -101.580785);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-11 18:19:00', 21.063137, -101.580615);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-11 18:19:30', 21.063109, -101.580509);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-11 18:20:00', 21.063073, -101.580361);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-11 18:20:30', 21.063, -101.580269);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-11 18:21:00', 21.062992, -101.580124);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-11 18:21:30', 21.062958, -101.580008);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-11 18:22:00', 21.062891, -101.579901);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-11 18:22:30', 21.062887, -101.579807);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-11 18:23:00', 21.06284, -101.579743);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-11 18:23:30', 21.062836, -101.579739);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-11 18:24:00', 21.062938, -101.580225);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-11 18:24:30', 21.063077, -101.580772);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-11 18:25:00', 21.063134, -101.580875);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-11 18:25:30', 21.063221, -101.581206);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-11 18:26:00', 21.063019, -101.58123);

INSERT INTO Operativo.Eventos_Detectados (RecorridoId, TipoEventoId, TimestampEvento, Latitud, Longitud, Geo_Es_Estimado) VALUES (@RecId, 5, '2026-07-11 18:11:36', 21.063367, -101.581615, 0);
INSERT INTO Operativo.Eventos_Detectados (RecorridoId, TipoEventoId, TimestampEvento, Latitud, Longitud, Geo_Es_Estimado) VALUES (@RecId, 4, '2026-07-11 18:18:18', 21.062975, -101.581559, 0);
INSERT INTO Operativo.Eventos_Detectados (RecorridoId, TipoEventoId, TimestampEvento, Latitud, Longitud, Geo_Es_Estimado) VALUES (@RecId, 5, '2026-07-11 18:08:15', 21.06331, -101.5816, 0);
INSERT INTO Operativo.Eventos_Detectados (RecorridoId, TipoEventoId, TimestampEvento, Latitud, Longitud, Geo_Es_Estimado) VALUES (@RecId, 4, '2026-07-11 18:24:09', 21.062959, -101.581562, 0);
GO

-- Recorrido mock v6 #12 (DispositivoId 10)
DECLARE @NewId TABLE (Id BIGINT);
INSERT INTO Operativo.Recorridos (DispositivoId, FechaInicio, FechaFin, Ruta_Coordenadas)
OUTPUT INSERTED.Id INTO @NewId
VALUES (10, '2026-07-12 17:31:00', '2026-07-12 17:49:00', NULL);

DECLARE @RecId BIGINT = (SELECT TOP 1 Id FROM @NewId);

INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-12 17:31:00', 21.062712, -101.581721);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-12 17:31:30', 21.062763, -101.581765);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-12 17:32:00', 21.062771, -101.581743);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-12 17:32:30', 21.062826, -101.581715);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-12 17:33:00', 21.062888, -101.581719);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-12 17:33:30', 21.062958, -101.581718);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-12 17:34:00', 21.062945, -101.581617);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-12 17:34:30', 21.063069, -101.581614);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-12 17:35:00', 21.063113, -101.581621);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-12 17:35:30', 21.063161, -101.581631);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-12 17:36:00', 21.063202, -101.58164);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-12 17:36:30', 21.063256, -101.581645);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-12 17:37:00', 21.063274, -101.581587);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-12 17:37:30', 21.063356, -101.581596);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-12 17:38:00', 21.063372, -101.581527);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-12 17:38:30', 21.063326, -101.581486);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-12 17:39:00', 21.063311, -101.581415);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-12 17:39:30', 21.063306, -101.581319);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-12 17:40:00', 21.063282, -101.581203);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-12 17:40:30', 21.063233, -101.581055);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-12 17:41:00', 21.063196, -101.580896);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-12 17:41:30', 21.063171, -101.580769);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-12 17:42:00', 21.063121, -101.58063);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-12 17:42:30', 21.063104, -101.580485);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-12 17:43:00', 21.063074, -101.580368);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-12 17:43:30', 21.063014, -101.580262);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-12 17:44:00', 21.062984, -101.580116);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-12 17:44:30', 21.062924, -101.580015);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-12 17:45:00', 21.062903, -101.579906);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-12 17:45:30', 21.062888, -101.579798);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-12 17:46:00', 21.062838, -101.579723);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-12 17:46:30', 21.062814, -101.579748);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-12 17:47:00', 21.062942, -101.580218);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-12 17:47:30', 21.063089, -101.580743);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-12 17:48:00', 21.063106, -101.58086);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-12 17:48:30', 21.063206, -101.581196);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-12 17:49:00', 21.063013, -101.581248);

INSERT INTO Operativo.Eventos_Detectados (RecorridoId, TipoEventoId, TimestampEvento, Latitud, Longitud, Geo_Es_Estimado) VALUES (@RecId, 5, '2026-07-12 17:40:41', 21.063372, -101.581529, 0);
INSERT INTO Operativo.Eventos_Detectados (RecorridoId, TipoEventoId, TimestampEvento, Latitud, Longitud, Geo_Es_Estimado) VALUES (@RecId, 4, '2026-07-12 17:35:26', 21.06295, -101.581573, 0);
INSERT INTO Operativo.Eventos_Detectados (RecorridoId, TipoEventoId, TimestampEvento, Latitud, Longitud, Geo_Es_Estimado) VALUES (@RecId, 5, '2026-07-12 17:47:44', 21.063357, -101.581562, 0);
INSERT INTO Operativo.Eventos_Detectados (RecorridoId, TipoEventoId, TimestampEvento, Latitud, Longitud, Geo_Es_Estimado) VALUES (@RecId, 4, '2026-07-12 17:31:18', 21.062886, -101.581602, 0);
GO

-- Recorrido mock v6 #13 (DispositivoId 10)
DECLARE @NewId TABLE (Id BIGINT);
INSERT INTO Operativo.Recorridos (DispositivoId, FechaInicio, FechaFin, Ruta_Coordenadas)
OUTPUT INSERTED.Id INTO @NewId
VALUES (10, '2026-07-13 19:05:00', '2026-07-13 19:23:00', NULL);

DECLARE @RecId BIGINT = (SELECT TOP 1 Id FROM @NewId);

INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-13 19:05:00', 21.062704, -101.58172);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-13 19:05:30', 21.062763, -101.581737);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-13 19:06:00', 21.062778, -101.581749);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-13 19:06:30', 21.062821, -101.581738);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-13 19:07:00', 21.062889, -101.581738);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-13 19:07:30', 21.062957, -101.581735);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-13 19:08:00', 21.062951, -101.581618);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-13 19:08:30', 21.063097, -101.581626);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-13 19:09:00', 21.063112, -101.581643);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-13 19:09:30', 21.063164, -101.581623);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-13 19:10:00', 21.063221, -101.581624);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-13 19:10:30', 21.063255, -101.581616);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-13 19:11:00', 21.06331, -101.581592);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-13 19:11:30', 21.063346, -101.581566);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-13 19:12:00', 21.063352, -101.581535);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-13 19:12:30', 21.063344, -101.581486);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-13 19:13:00', 21.063321, -101.581411);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-13 19:13:30', 21.063294, -101.581321);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-13 19:14:00', 21.063287, -101.581173);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-13 19:14:30', 21.063265, -101.58106);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-13 19:15:00', 21.063202, -101.580883);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-13 19:15:30', 21.063152, -101.580761);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-13 19:16:00', 21.063124, -101.580624);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-13 19:16:30', 21.063083, -101.580503);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-13 19:17:00', 21.063045, -101.580377);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-13 19:17:30', 21.063024, -101.580261);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-13 19:18:00', 21.062961, -101.580123);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-13 19:18:30', 21.062928, -101.580015);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-13 19:19:00', 21.062896, -101.579911);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-13 19:19:30', 21.062859, -101.579792);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-13 19:20:00', 21.062875, -101.57974);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-13 19:20:30', 21.062826, -101.579732);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-13 19:21:00', 21.062935, -101.580229);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-13 19:21:30', 21.063105, -101.58074);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-13 19:22:00', 21.063128, -101.580876);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-13 19:22:30', 21.063216, -101.581189);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-13 19:23:00', 21.063047, -101.581227);

INSERT INTO Operativo.Eventos_Detectados (RecorridoId, TipoEventoId, TimestampEvento, Latitud, Longitud, Geo_Es_Estimado) VALUES (@RecId, 5, '2026-07-13 19:23:00', 21.063305, -101.581592, 0);
INSERT INTO Operativo.Eventos_Detectados (RecorridoId, TipoEventoId, TimestampEvento, Latitud, Longitud, Geo_Es_Estimado) VALUES (@RecId, 4, '2026-07-13 19:07:09', 21.062894, -101.581561, 0);
INSERT INTO Operativo.Eventos_Detectados (RecorridoId, TipoEventoId, TimestampEvento, Latitud, Longitud, Geo_Es_Estimado) VALUES (@RecId, 5, '2026-07-13 19:20:15', 21.063334, -101.581603, 0);
GO

-- Recorrido mock v6 #14 (DispositivoId 10)
DECLARE @NewId TABLE (Id BIGINT);
INSERT INTO Operativo.Recorridos (DispositivoId, FechaInicio, FechaFin, Ruta_Coordenadas)
OUTPUT INSERTED.Id INTO @NewId
VALUES (10, '2026-07-14 20:41:00', '2026-07-14 20:59:00', NULL);

DECLARE @RecId BIGINT = (SELECT TOP 1 Id FROM @NewId);

INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-14 20:41:00', 21.062698, -101.581719);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-14 20:41:30', 21.062762, -101.581733);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-14 20:42:00', 21.062782, -101.581748);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-14 20:42:30', 21.062844, -101.581721);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-14 20:43:00', 21.062872, -101.581716);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-14 20:43:30', 21.062952, -101.581713);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-14 20:44:00', 21.062944, -101.581626);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-14 20:44:30', 21.063099, -101.581636);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-14 20:45:00', 21.063121, -101.581622);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-14 20:45:30', 21.063183, -101.581652);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-14 20:46:00', 21.063211, -101.581629);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-14 20:46:30', 21.063229, -101.58162);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-14 20:47:00', 21.063277, -101.581611);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-14 20:47:30', 21.063339, -101.581592);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-14 20:48:00', 21.063372, -101.581549);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-14 20:48:30', 21.063361, -101.581485);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-14 20:49:00', 21.06333, -101.581393);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-14 20:49:30', 21.063308, -101.581322);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-14 20:50:00', 21.063278, -101.58118);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-14 20:50:30', 21.063233, -101.581084);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-14 20:51:00', 21.063215, -101.580892);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-14 20:51:30', 21.063155, -101.58077);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-14 20:52:00', 21.063115, -101.580599);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-14 20:52:30', 21.063095, -101.58052);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-14 20:53:00', 21.063068, -101.580391);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-14 20:53:30', 21.063011, -101.580276);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-14 20:54:00', 21.062986, -101.580138);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-14 20:54:30', 21.06294, -101.58002);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-14 20:55:00', 21.062907, -101.579899);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-14 20:55:30', 21.062877, -101.5798);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-14 20:56:00', 21.062856, -101.579739);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-14 20:56:30', 21.062821, -101.579765);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-14 20:57:00', 21.062952, -101.580226);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-14 20:57:30', 21.063108, -101.580736);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-14 20:58:00', 21.063105, -101.580876);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-14 20:58:30', 21.063227, -101.581201);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-14 20:59:00', 21.063012, -101.581231);

INSERT INTO Operativo.Eventos_Detectados (RecorridoId, TipoEventoId, TimestampEvento, Latitud, Longitud, Geo_Es_Estimado) VALUES (@RecId, 5, '2026-07-14 20:54:45', 21.063307, -101.581529, 0);
INSERT INTO Operativo.Eventos_Detectados (RecorridoId, TipoEventoId, TimestampEvento, Latitud, Longitud, Geo_Es_Estimado) VALUES (@RecId, 4, '2026-07-14 20:47:07', 21.062908, -101.58158, 0);
GO

-- Recorrido mock v6 #15 (DispositivoId 10)
DECLARE @NewId TABLE (Id BIGINT);
INSERT INTO Operativo.Recorridos (DispositivoId, FechaInicio, FechaFin, Ruta_Coordenadas)
OUTPUT INSERTED.Id INTO @NewId
VALUES (10, '2026-07-15 18:39:00', '2026-07-15 18:57:00', NULL);

DECLARE @RecId BIGINT = (SELECT TOP 1 Id FROM @NewId);

INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-15 18:39:00', 21.062732, -101.581747);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-15 18:39:30', 21.062765, -101.581765);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-15 18:40:00', 21.06281, -101.581757);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-15 18:40:30', 21.06285, -101.58172);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-15 18:41:00', 21.062894, -101.581703);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-15 18:41:30', 21.062946, -101.58173);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-15 18:42:00', 21.062967, -101.581624);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-15 18:42:30', 21.063074, -101.581641);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-15 18:43:00', 21.063145, -101.581619);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-15 18:43:30', 21.06319, -101.581649);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-15 18:44:00', 21.063226, -101.581636);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-15 18:44:30', 21.063231, -101.581628);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-15 18:45:00', 21.063289, -101.581621);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-15 18:45:30', 21.063359, -101.581586);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-15 18:46:00', 21.063356, -101.581528);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-15 18:46:30', 21.063347, -101.581487);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-15 18:47:00', 21.063341, -101.581388);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-15 18:47:30', 21.063301, -101.581288);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-15 18:48:00', 21.063255, -101.581199);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-15 18:48:30', 21.063233, -101.58105);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-15 18:49:00', 21.063208, -101.580884);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-15 18:49:30', 21.063158, -101.580768);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-15 18:50:00', 21.063141, -101.580627);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-15 18:50:30', 21.06308, -101.580522);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-15 18:51:00', 21.063054, -101.580361);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-15 18:51:30', 21.063022, -101.580261);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-15 18:52:00', 21.062976, -101.580136);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-15 18:52:30', 21.062957, -101.58001);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-15 18:53:00', 21.062897, -101.579914);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-15 18:53:30', 21.062889, -101.579805);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-15 18:54:00', 21.062873, -101.579743);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-15 18:54:30', 21.062815, -101.579766);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-15 18:55:00', 21.062969, -101.580203);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-15 18:55:30', 21.063092, -101.580769);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-15 18:56:00', 21.063122, -101.580867);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-15 18:56:30', 21.063233, -101.581187);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-15 18:57:00', 21.063041, -101.581248);

INSERT INTO Operativo.Eventos_Detectados (RecorridoId, TipoEventoId, TimestampEvento, Latitud, Longitud, Geo_Es_Estimado) VALUES (@RecId, 5, '2026-07-15 18:53:13', 21.06338, -101.581551, 0);
INSERT INTO Operativo.Eventos_Detectados (RecorridoId, TipoEventoId, TimestampEvento, Latitud, Longitud, Geo_Es_Estimado) VALUES (@RecId, 4, '2026-07-15 18:45:47', 21.062938, -101.581622, 0);
INSERT INTO Operativo.Eventos_Detectados (RecorridoId, TipoEventoId, TimestampEvento, Latitud, Longitud, Geo_Es_Estimado) VALUES (@RecId, 5, '2026-07-15 18:46:03', 21.063315, -101.581557, 0);
GO

-- Recorrido mock v6 #16 (DispositivoId 10)
DECLARE @NewId TABLE (Id BIGINT);
INSERT INTO Operativo.Recorridos (DispositivoId, FechaInicio, FechaFin, Ruta_Coordenadas)
OUTPUT INSERTED.Id INTO @NewId
VALUES (10, '2026-07-01 17:52:00', '2026-07-01 18:00:00', NULL);

DECLARE @RecId BIGINT = (SELECT TOP 1 Id FROM @NewId);

INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-01 17:52:00', 21.062708, -101.581728);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-01 17:52:30', 21.062753, -101.581753);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-01 17:53:00', 21.062787, -101.581732);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-01 17:53:30', 21.062825, -101.581722);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-01 17:54:00', 21.06286, -101.581731);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-01 17:54:30', 21.062878, -101.581751);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-01 17:55:00', 21.06315, -101.581785);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-01 17:55:30', 21.0632, -101.58178);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-01 17:56:00', 21.063198, -101.581839);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-01 17:56:30', 21.063247, -101.581871);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-01 17:57:00', 21.063258, -101.581923);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-01 17:57:30', 21.063338, -101.581981);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-01 17:58:00', 21.06339, -101.582063);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-01 17:58:30', 21.063505, -101.582281);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-01 17:59:00', 21.063547, -101.582473);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-01 17:59:30', 21.0635, -101.582461);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-01 18:00:00', 21.063339, -101.582561);

INSERT INTO Operativo.Eventos_Detectados (RecorridoId, TipoEventoId, TimestampEvento, Latitud, Longitud, Geo_Es_Estimado) VALUES (@RecId, 5, '2026-07-01 17:55:17', 21.063321, -101.581906, 0);
INSERT INTO Operativo.Eventos_Detectados (RecorridoId, TipoEventoId, TimestampEvento, Latitud, Longitud, Geo_Es_Estimado) VALUES (@RecId, 5, '2026-07-01 17:53:01', 21.063404, -101.581883, 0);
GO

-- Recorrido mock v6 #17 (DispositivoId 10)
DECLARE @NewId TABLE (Id BIGINT);
INSERT INTO Operativo.Recorridos (DispositivoId, FechaInicio, FechaFin, Ruta_Coordenadas)
OUTPUT INSERTED.Id INTO @NewId
VALUES (10, '2026-07-02 18:01:00', '2026-07-02 18:09:00', NULL);

DECLARE @RecId BIGINT = (SELECT TOP 1 Id FROM @NewId);

INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-02 18:01:00', 21.062714, -101.581715);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-02 18:01:30', 21.062774, -101.581759);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-02 18:02:00', 21.062802, -101.58173);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-02 18:02:30', 21.062841, -101.581743);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-02 18:03:00', 21.062861, -101.581728);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-02 18:03:30', 21.062895, -101.581747);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-02 18:04:00', 21.06314, -101.581784);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-02 18:04:30', 21.063202, -101.58178);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-02 18:05:00', 21.063204, -101.581835);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-02 18:05:30', 21.063217, -101.581865);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-02 18:06:00', 21.063292, -101.581935);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-02 18:06:30', 21.063341, -101.581971);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-02 18:07:00', 21.063419, -101.582067);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-02 18:07:30', 21.063517, -101.582278);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-02 18:08:00', 21.063559, -101.582478);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-02 18:08:30', 21.063477, -101.582461);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-02 18:09:00', 21.063346, -101.582523);

INSERT INTO Operativo.Eventos_Detectados (RecorridoId, TipoEventoId, TimestampEvento, Latitud, Longitud, Geo_Es_Estimado) VALUES (@RecId, 5, '2026-07-02 18:03:08', 21.063381, -101.581948, 0);
INSERT INTO Operativo.Eventos_Detectados (RecorridoId, TipoEventoId, TimestampEvento, Latitud, Longitud, Geo_Es_Estimado) VALUES (@RecId, 5, '2026-07-02 18:08:22', 21.063407, -101.581912, 0);
INSERT INTO Operativo.Eventos_Detectados (RecorridoId, TipoEventoId, TimestampEvento, Latitud, Longitud, Geo_Es_Estimado) VALUES (@RecId, 5, '2026-07-02 18:03:48', 21.063392, -101.581889, 0);
GO

-- Recorrido mock v6 #18 (DispositivoId 10)
DECLARE @NewId TABLE (Id BIGINT);
INSERT INTO Operativo.Recorridos (DispositivoId, FechaInicio, FechaFin, Ruta_Coordenadas)
OUTPUT INSERTED.Id INTO @NewId
VALUES (10, '2026-07-03 16:49:00', '2026-07-03 16:57:00', NULL);

DECLARE @RecId BIGINT = (SELECT TOP 1 Id FROM @NewId);

INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-03 16:49:00', 21.062701, -101.581721);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-03 16:49:30', 21.062749, -101.581763);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-03 16:50:00', 21.062791, -101.581738);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-03 16:50:30', 21.062834, -101.581729);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-03 16:51:00', 21.062871, -101.581733);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-03 16:51:30', 21.062893, -101.581744);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-03 16:52:00', 21.063147, -101.581766);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-03 16:52:30', 21.063203, -101.58178);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-03 16:53:00', 21.063197, -101.581866);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-03 16:53:30', 21.063244, -101.581875);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-03 16:54:00', 21.063265, -101.581914);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-03 16:54:30', 21.063348, -101.58196);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-03 16:55:00', 21.06339, -101.582063);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-03 16:55:30', 21.063495, -101.582274);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-03 16:56:00', 21.063542, -101.582461);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-03 16:56:30', 21.063496, -101.582475);
INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) VALUES (@RecId, '2026-07-03 16:57:00', 21.063348, -101.58253);

INSERT INTO Operativo.Eventos_Detectados (RecorridoId, TipoEventoId, TimestampEvento, Latitud, Longitud, Geo_Es_Estimado) VALUES (@RecId, 5, '2026-07-03 16:56:12', 21.063357, -101.581927, 0);
INSERT INTO Operativo.Eventos_Detectados (RecorridoId, TipoEventoId, TimestampEvento, Latitud, Longitud, Geo_Es_Estimado) VALUES (@RecId, 5, '2026-07-03 16:50:16', 21.063387, -101.581902, 0);
INSERT INTO Operativo.Eventos_Detectados (RecorridoId, TipoEventoId, TimestampEvento, Latitud, Longitud, Geo_Es_Estimado) VALUES (@RecId, 5, '2026-07-03 16:50:22', 21.063354, -101.581935, 0);
INSERT INTO Operativo.Eventos_Detectados (RecorridoId, TipoEventoId, TimestampEvento, Latitud, Longitud, Geo_Es_Estimado) VALUES (@RecId, 5, '2026-07-03 16:50:58', 21.063333, -101.581916, 0);
GO

-- Verificacion
SELECT COUNT(*) AS TotalRecorridos FROM Operativo.Recorridos;
SELECT COUNT(*) AS TotalCoordenadas FROM Operativo.RecorridoCoordenadas;
SELECT COUNT(*) AS TotalEventos FROM Operativo.Eventos_Detectados;