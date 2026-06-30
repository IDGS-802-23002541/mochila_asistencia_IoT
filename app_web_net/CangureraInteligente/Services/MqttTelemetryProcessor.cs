using CangureraInteligente.Data;
using CangureraInteligente.DTOs;
using CangureraInteligente.Models;
using Microsoft.EntityFrameworkCore;

namespace CangureraInteligente.Services;

/// <summary>
/// Implementación del procesador de mensajes MQTT del ESP32.
/// Trabaja directamente sobre el DbContext (mismo patrón que RecorridosController),
/// ya que el proyecto no tiene un servicio de dominio separado para Recorridos/Eventos.
/// </summary>
public class MqttTelemetryProcessor : IMqttTelemetryProcessor
{
    private readonly CangureraDbContext _db;
    private readonly ILogger<MqttTelemetryProcessor> _log;
    private readonly IMqttPublisherService _publisher;
    private readonly ZonaCalienteAlertState _alertState;

    public MqttTelemetryProcessor(
        CangureraDbContext db,
        ILogger<MqttTelemetryProcessor> log,
        IMqttPublisherService publisher,
        ZonaCalienteAlertState alertState)
    {
        _db = db;
        _log = log;
        _publisher = publisher;
        _alertState = alertState;
    }

    public async Task<bool> ProcesarTelemetriaAsync(MqttTelemetryPayload payload, CancellationToken ct = default)
    {
        try
        {
            var dispositivo = await _db.Dispositivos
                .FirstOrDefaultAsync(d => d.MacAddress == payload.MacAddress, ct);

            if (dispositivo is null)
            {
                _log.LogWarning("Telemetría: el dispositivo {Id} no existe.", payload.MacAddress);
                return false;
            }

            dispositivo.UltimaConexion = payload.Fecha;
            await _db.SaveChangesAsync(ct);

            return true;
        }
        catch (Exception ex)
        {
            _log.LogError(ex, "Error al procesar telemetría del dispositivo {Mac}", payload.MacAddress);
            return false;
        }
    }

    public async Task<bool> RegistrarEventoAsync(MqttEventoPayload payload, CancellationToken ct = default)
    {
        try
        {
            var recorrido = await _db.Recorridos
                .FirstOrDefaultAsync(r => r.Id == payload.RecorridoId, ct);

            if (recorrido is null)
            {
                _log.LogWarning("Registrar evento: el recorrido {Id} no existe.", payload.RecorridoId);
                return false;
            }

            if (recorrido.FechaFin is not null)
            {
                _log.LogWarning("Registrar evento: el recorrido {Id} ya está cerrado; se descarta el evento.", payload.RecorridoId);
                return false;
            }

            bool tipoExiste = await _db.TiposEvento.AnyAsync(t => t.Id == payload.TipoEventoId, ct);
            if (!tipoExiste)
            {
                _log.LogWarning("Registrar evento: TipoEventoId {Id} no existe en el catálogo.", payload.TipoEventoId);
                return false;
            }

            var evento = new EventoDetectado
            {
                RecorridoId     = payload.RecorridoId,
                TipoEventoId    = payload.TipoEventoId,
                TimeStampEvento = payload.Timestamp ?? DateTime.UtcNow,
                Latitud         = payload.Latitud,
                Longitud        = payload.Longitud,
                Geo_Es_Estimado = payload.GeoEsEstimado,
                FuerzaImpactoG  = payload.FuerzaImpactoG,
                IrIzquierdo     = payload.IrIzquierdo,
                IrDerecho       = payload.IrDerecho,
                DistanciaCm     = payload.Dist
            };

            _db.EventosDetectados.Add(evento);
            await _db.SaveChangesAsync(ct);

            _log.LogInformation("Evento (tipo {TipoId}) registrado para recorrido {RecId}",
                payload.TipoEventoId, payload.RecorridoId);

            return true;
        }
        catch (Exception ex)
        {
            _log.LogError(ex, "Error al registrar evento para recorrido {Id}", payload.RecorridoId);
            return false;
        }
    }

    public async Task<bool> FinalizarRecorridoAsync(MqttFinalizarRecorridoPayload payload, CancellationToken ct = default)
    {
        try
        {
            var recorrido = await _db.Recorridos
                .FirstOrDefaultAsync(r => r.Id == payload.RecorridoId, ct);

            if (recorrido is null)
            {
                _log.LogWarning("Finalizar recorrido: el recorrido {Id} no existe.", payload.RecorridoId);
                return false;
            }

            if (recorrido.FechaFin is not null)
            {
                // Idempotente: evita reprocesar si el broker reentrega el mensaje (QoS 1).
                _log.LogInformation("Finalizar recorrido: el recorrido {Id} ya estaba cerrado; se ignora.", payload.RecorridoId);
                return true;
            }

            recorrido.FechaFin = payload.FechaFin;
            recorrido.Ruta_Coordenadas = payload.RutaCoordenadas;

            await _db.SaveChangesAsync(ct);

            _log.LogInformation("Recorrido {Id} finalizado.", payload.RecorridoId);

            return true;
        }
        catch (Exception ex)
        {
            // Si Ruta_Coordenadas no es JSON válido, el CHECK ISJSON de la BD rechaza el SaveChanges.
            _log.LogError(ex, "Error al finalizar recorrido {Id}", payload.RecorridoId);
            return false;
        }
    }

private async Task EvaluarZonasCalientesAsync(int dispositivoId, decimal lat, decimal lon, CancellationToken ct)
{
    var zonas = await _db.ZonasCalientes.Where(z => z.Activa).ToListAsync(ct);
    var zonasDentroAhora = new List<int>();

    foreach (var zona in zonas)
    {
        var distancia = GeoUtil.DistanciaMetros((double)lat, (double)lon, (double)zona.Latitud, (double)zona.Longitud);
        if (distancia > zona.RadioMetros) continue;

        zonasDentroAhora.Add(zona.Id);

        if (!_alertState.YaAlertado(dispositivoId, zona.Id))
        {
            var alerta = new ZonaCalienteAlertaPayload
            {
                DispositivoId   = dispositivoId,
                TipoEventoId    = zona.TipoEventoId,
                Latitud         = lat,
                Longitud        = lon,
                DistanciaMetros = Math.Round(distancia, 1)
            };

            await _publisher.PublicarAlertaZonaCalienteAsync(alerta, ct);
        }
    }

    _alertState.ActualizarZonasActuales(dispositivoId, zonasDentroAhora);
}

}