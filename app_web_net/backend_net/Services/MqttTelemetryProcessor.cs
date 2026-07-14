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

	private readonly IMqttPublisherService _publisher;

	private readonly ZonaCalienteAlertState _alertState;

	public MqttTelemetryProcessor(CangureraDbContext db, ILogger<MqttTelemetryProcessor> log, IMqttPublisherService publisher, ZonaCalienteAlertState alertState)
	{
		_db = db;
		_log = log;
		_publisher = publisher;
		_alertState = alertState;
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
			await _db.SaveChangesAsync(ct);
			if (payload.Latitud.HasValue && payload.Longitud.HasValue)
			{
				await EvaluarZonasCalientesAsync(dispositivo.Id, payload.Latitud.Value, payload.Longitud.Value, ct);
			}
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
			if (payload.Latitud.HasValue && payload.Longitud.HasValue)
			{
				await EvaluarZonasCalientesAsync(recorrido.DispositivoId, payload.Latitud.Value, payload.Longitud.Value, ct);
			}
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
			recorrido.Ruta_Coordenadas = payload.RutaCoordenadas;
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

	private async Task EvaluarZonasCalientesAsync(int dispositivoId, decimal lat, decimal lon, CancellationToken ct)
	{
		Dispositivo dispositivo = await _db.Dispositivos.AsNoTracking().FirstOrDefaultAsync((Dispositivo d) => d.Id == dispositivoId, ct);
		List<ZonaCaliente> list = await _db.ZonasCalientes.Where((ZonaCaliente z) => z.Activa).ToListAsync(ct);
		List<int> zonasDentroAhora = new List<int>();
		foreach (ZonaCaliente item in list)
		{
			double num = GeoUtil.DistanciaMetros((double)lat, (double)lon, (double)item.Latitud, (double)item.Longitud);
			if (!(num > item.RadioMetros))
			{
				zonasDentroAhora.Add(item.Id);
				if (!_alertState.YaAlertado(dispositivoId, item.Id))
				{
					ZonaCalienteAlertaPayload payload = new ZonaCalienteAlertaPayload
					{
						MacAddress = (dispositivo?.MacAddress ?? string.Empty),
						Mensaje = "acercandose_zona_caliente",
						TipoEventoId = item.TipoEventoPredominanteId.GetValueOrDefault(),
						Latitud = lat,
						Longitud = lon,
						DistanciaMetros = Math.Round(num, 1)
					};
					await _publisher.PublicarAlertaZonaCalienteAsync(payload, ct);
				}
			}
		}
		_alertState.ActualizarZonasActuales(dispositivoId, zonasDentroAhora);
	}
}
