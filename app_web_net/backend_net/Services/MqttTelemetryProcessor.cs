using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading;
using System.Threading.Tasks;
using CangureraInteligente.DTOs;
using CangureraInteligente.Data;
using CangureraInteligente.Models;
using Microsoft.EntityFrameworkCore;
using Microsoft.Extensions.Logging;

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

		public MqttTelemetryProcessor(CangureraDbContext db, ILogger<MqttTelemetryProcessor> log)
	{
		_db = db;
		_log = log;
	}

	public async Task<bool> ProcesarTelemetriaAsync(MqttTelemetryPayload payload, CancellationToken ct = default(CancellationToken))
	{
		try
		{
			Dispositivo dispositivo = await _db.Dispositivos.FirstOrDefaultAsync((Dispositivo d) => d.MacAddress == payload.MacAddress, ct);
			if (dispositivo == null)
			{
				_log.LogWarning("Telemetría: el dispositivo {Id} no existe.", payload.MacAddress);
				return false;
			}
			dispositivo.UltimaConexion = payload.Fecha;
			Recorrido recorrido = await _db.Recorridos.FirstOrDefaultAsync((Recorrido r) => r.DispositivoId == dispositivo.Id && r.FechaFin == null, ct);
			if (recorrido != null && payload.Latitud.HasValue && payload.Longitud.HasValue)
			{
				_db.RecorridoCoordenadas.Add(new RecorridoCoordenada
				{
					RecorridoId = recorrido.Id,
					Fecha = payload.Fecha,
					Latitud = payload.Latitud.Value,
					Longitud = payload.Longitud.Value
				});
			}
			await _db.SaveChangesAsync(ct);
			return true;
		}
		catch (Exception exception)
		{
			_log.LogError(exception, "Error al procesar telemetría del dispositivo {Mac}", payload.MacAddress);
			return false;
		}
	}

	public async Task<bool> RegistrarEventoAsync(MqttEventoPayload payload, CancellationToken ct = default(CancellationToken))
	{
		try
		{
			Recorrido recorrido = await _db.Recorridos.FirstOrDefaultAsync((Recorrido r) => r.Id == payload.RecorridoId, ct);
			if (recorrido == null)
			{
				_log.LogWarning("Registrar evento: el recorrido {Id} no existe.", payload.RecorridoId);
				return false;
			}
			if (recorrido.FechaFin.HasValue)
			{
				_log.LogWarning("Registrar evento: el recorrido {Id} ya está cerrado; se descarta el evento.", payload.RecorridoId);
				return false;
			}
			if (!(await _db.TiposEvento.AnyAsync((CatTipoEvento t) => t.Id == payload.TipoEventoId, ct)))
			{
				_log.LogWarning("Registrar evento: TipoEventoId {Id} no existe en el catálogo.", payload.TipoEventoId);
				return false;
			}
			EventoDetectado entity = new EventoDetectado
			{
				RecorridoId = payload.RecorridoId,
				TipoEventoId = payload.TipoEventoId,
				TimestampEvento = (payload.Timestamp ?? DateTime.UtcNow),
				Latitud = payload.Latitud,
				Longitud = payload.Longitud,
				Geo_Es_Estimado = payload.GeoEsEstimado,
				FuerzaImpactoG = payload.FuerzaImpactoG,
				IrIzquierdo = payload.IrIzquierdo,
				IrDerecho = payload.IrDerecho,
				DistanciaCm = payload.Dist
			};
			_db.EventosDetectados.Add(entity);
			await _db.SaveChangesAsync(ct);
			_log.LogInformation("Evento (tipo {TipoId}) registrado para recorrido {RecId}", payload.TipoEventoId, payload.RecorridoId);
			return true;
		}
		catch (Exception exception)
		{
			_log.LogError(exception, "Error al registrar evento para recorrido {Id}", payload.RecorridoId);
			return false;
		}
	}

	public async Task<bool> FinalizarRecorridoAsync(MqttFinalizarRecorridoPayload payload, CancellationToken ct = default(CancellationToken))
	{
		try
		{
			Recorrido recorrido = await _db.Recorridos.FirstOrDefaultAsync((Recorrido r) => r.Id == payload.RecorridoId, ct);
			if (recorrido == null)
			{
				_log.LogWarning("Finalizar recorrido: el recorrido {Id} no existe.", payload.RecorridoId);
				return false;
			}
			if (recorrido.FechaFin.HasValue)
			{
				_log.LogInformation("Finalizar recorrido: el recorrido {Id} ya estaba cerrado; se ignora.", payload.RecorridoId);
				return true;
			}
			recorrido.FechaFin = payload.FechaFin;
			await _db.SaveChangesAsync(ct);
			_log.LogInformation("Recorrido {Id} finalizado.", payload.RecorridoId);
			return true;
		}
		catch (Exception exception)
		{
			_log.LogError(exception, "Error al finalizar recorrido {Id}", payload.RecorridoId);
			return false;
		}
	}

}
