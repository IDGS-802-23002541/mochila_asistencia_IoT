using System;
using System.Collections.Generic;
using System.Linq;
using System.Text.Json;
using System.Threading;
using System.Threading.Tasks;
using CangureraInteligente.DTOs;
using CangureraInteligente.Data;
using CangureraInteligente.Models;
using CangureraInteligente.Services;
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using Microsoft.Extensions.Logging;

namespace CangureraInteligente.Controllers;

/// <summary>
/// Endpoints HTTP consumidos por la app móvil (préstamo de mochila).
/// Base URL: /api/recorridos
/// </summary>
[ApiController]
[Route("api/recorridos")]
[Produces("application/json", new string[] { })]
public class RecorridosController(CangureraDbContext db, ILogger<RecorridosController> log) : ControllerBase
{
	[HttpGet]
	[ProducesResponseType(typeof(List<RecorridoHistorialResponse>), 200)]
	public async Task<IActionResult> GetAll([FromQuery] int? organizacionId, CancellationToken ct)
	{
		IQueryable<Recorrido> query = db.Recorridos.AsNoTracking().Include((Recorrido r) => r.Dispositivo).Include((Recorrido r) => r.Eventos);
		if (organizacionId.HasValue)
		{
			if (!(await db.Organizaciones.AnyAsync((Organizacion o) => o.Id == organizacionId.Value, ct)))
			{
				return NotFound(new
				{
					error = $"La organización {organizacionId.Value} no existe."
				});
			}
			query = query.Where((Recorrido r) => r.Dispositivo.OrganizacionId == organizacionId.Value);
		}

		List<Recorrido> recorridos = await query.OrderByDescending((Recorrido r) => r.FechaInicio).ToListAsync(ct);
		var respuesta = recorridos.Select((Recorrido r) =>
		{
			var coordenadas = new List<CoordenadaGps>();
			if (!string.IsNullOrWhiteSpace(r.Ruta_Coordenadas))
			{
				try
				{
					coordenadas = JsonSerializer.Deserialize<List<CoordenadaGps>>(r.Ruta_Coordenadas, new JsonSerializerOptions
					{
						PropertyNameCaseInsensitive = true
					}) ?? new List<CoordenadaGps>();
				}
				catch (JsonException)
				{
					coordenadas = new List<CoordenadaGps>();
				}
			}

			var resumen = CalcularResumen(coordenadas, r.Id);
			return new RecorridoHistorialResponse
			{
				Id = r.Id,
				DispositivoMac = r.Dispositivo?.MacAddress ?? string.Empty,
				FechaInicio = r.FechaInicio,
				FechaFin = r.FechaFin,
				DuracionSegundos = resumen.DuracionSegundos ?? 0,
				TotalEventos = r.Eventos?.Count ?? 0,
				DistanciaTotalMetros = resumen.DistanciaTotalMetros
			};
		}).ToList();

		return Ok(respuesta);
	}

	[HttpPost("iniciar")]
	[ProducesResponseType(typeof(IniciarRecorridoResponse), 201)]
	[ProducesResponseType(400)]
	[ProducesResponseType(404)]
	[ProducesResponseType(409)]
	public async Task<IActionResult> IniciarRecorrido([FromBody] IniciarRecorridoRequest req, CancellationToken ct)
	{
		Dispositivo dispositivo = await db.Dispositivos.Include((Dispositivo d) => d.Organizacion).FirstOrDefaultAsync((Dispositivo d) => d.MacAddress == req.DispositivoMac, ct);
		if (dispositivo == null)
		{
			return NotFound(new
			{
				error = "Dispositivo con MAC '" + req.DispositivoMac + "' no encontrado."
			});
		}
		if (dispositivo.Estado != "Activo")
		{
			return Conflict(new
			{
				error = $"El dispositivo '{req.DispositivoMac}' no está activo (estado: {dispositivo.Estado})."
			});
		}
		if (await db.Recorridos.AnyAsync((Recorrido r) => r.DispositivoId == dispositivo.Id && r.FechaFin == null, ct))
		{
			return Conflict(new
			{
				error = "El dispositivo ya tiene un recorrido activo sin cerrar."
			});
		}
		if (req.DiscapacidadId.HasValue && !(await db.TiposDiscapacidad.AnyAsync((CatTipoDiscapacidad d) => d.Id == req.DiscapacidadId.Value, ct)))
		{
			return BadRequest(new
			{
				error = $"DiscapacidadId {req.DiscapacidadId} no existe en el catálogo."
			});
		}
		Recorrido recorrido = new Recorrido
		{
			DispositivoId = dispositivo.Id,
			FechaInicio = DateTime.UtcNow,
			Usuario_Edad = req.UsuarioEdad,
			DiscapacidadId = req.DiscapacidadId
		};
		db.Recorridos.Add(recorrido);
		dispositivo.UltimaConexion = DateTime.UtcNow;
		await db.SaveChangesAsync(ct);
		log.LogInformation("Recorrido {RecorridoId} iniciado para dispositivo {Mac} (Org: {Org})", recorrido.Id, dispositivo.MacAddress, dispositivo.Organizacion.Nombre);
		return CreatedAtAction("GetRecorrido", new
		{
			id = recorrido.Id
		}, new IniciarRecorridoResponse
		{
			RecorridoId = recorrido.Id,
			DispositivoMac = dispositivo.MacAddress,
			FechaInicio = recorrido.FechaInicio
		});
	}

	[HttpGet("dispositivo/{mac}")]
	[ProducesResponseType(typeof(List<RecorridoHistorialResponse>), 200)]
	[ProducesResponseType(404)]
	public async Task<IActionResult> GetRecorridosPorDispositivo(string mac, CancellationToken ct)
	{
		Dispositivo dispositivo = await db.Dispositivos
			.AsNoTracking()
			.FirstOrDefaultAsync((Dispositivo d) => d.MacAddress == mac, ct);
		if (dispositivo == null)
		{
			return NotFound(new
			{
				error = $"Dispositivo con MAC '{mac}' no encontrado."
			});
		}

		List<Recorrido> recorridos = await db.Recorridos
			.AsNoTracking()
			.Where((Recorrido r) => r.DispositivoId == dispositivo.Id)
			.OrderByDescending((Recorrido r) => r.FechaInicio)
			.ToListAsync(ct);

		List<RecorridoHistorialResponse> respuesta = new List<RecorridoHistorialResponse>();
		foreach (Recorrido recorrido in recorridos)
		{
			List<CoordenadaGps> coordenadas = new List<CoordenadaGps>();
			if (!string.IsNullOrWhiteSpace(recorrido.Ruta_Coordenadas))
			{
				try
				{
					coordenadas = JsonSerializer.Deserialize<List<CoordenadaGps>>(recorrido.Ruta_Coordenadas, new JsonSerializerOptions
					{
						PropertyNameCaseInsensitive = true
					}) ?? new List<CoordenadaGps>();
				}
				catch (JsonException)
				{
					coordenadas = new List<CoordenadaGps>();
				}
			}

			ResumenRecorridoResponse resumen = CalcularResumen(coordenadas, recorrido.Id);
			respuesta.Add(new RecorridoHistorialResponse
			{
				Id = recorrido.Id,
				DispositivoMac = dispositivo.MacAddress,
				FechaInicio = recorrido.FechaInicio,
				FechaFin = recorrido.FechaFin,
				DuracionSegundos = resumen.DuracionSegundos ?? 0,
				TotalEventos = recorrido.Eventos?.Count ?? 0,
				DistanciaTotalMetros = resumen.DistanciaTotalMetros
			});
		}

		return Ok(respuesta);
	}

	[HttpGet("{id:int}")]
	[ProducesResponseType(typeof(RecorridoDetalleResponse), 200)]
	[ProducesResponseType(404)]
	public async Task<IActionResult> GetRecorrido(int id, CancellationToken ct)
	{
		Recorrido recorrido = await db.Recorridos.Include((Recorrido r) => r.Dispositivo).ThenInclude((Dispositivo d) => d.Organizacion).Include((Recorrido r) => r.Discapacidad)
			.Include((Recorrido r) => r.Eventos)
			.FirstOrDefaultAsync((Recorrido r) => r.Id == id, ct);
		if (recorrido == null)
		{
			return NotFound(new
			{
				error = $"Recorrido {id} no encontrado."
			});
		}
		return Ok(new RecorridoDetalleResponse
		{
			Id = recorrido.Id,
			DispositivoMac = recorrido.Dispositivo.MacAddress,
			Organizacion = recorrido.Dispositivo.Organizacion.Nombre,
			FechaInicio = recorrido.FechaInicio,
			FechaFin = recorrido.FechaFin,
			UsuarioEdad = recorrido.Usuario_Edad,
			Discapacidad = recorrido.Discapacidad?.Nombre,
			TotalEventos = recorrido.Eventos.Count
		});
	}

	[HttpGet("{id:int}/resumen")]
	[ProducesResponseType(typeof(ResumenRecorridoResponse), 200)]
	[ProducesResponseType(404)]
	[ProducesResponseType(400)]
	public async Task<IActionResult> ResumenRecorrido(int id, CancellationToken ct)
	{
		Recorrido recorrido = await db.Recorridos.AsNoTracking().FirstOrDefaultAsync((Recorrido r) => r.Id == id, ct);
		if (recorrido == null)
		{
			return NotFound(new
			{
				error = $"Recorrido {id} no encontrado."
			});
		}
		if (string.IsNullOrWhiteSpace(recorrido.Ruta_Coordenadas))
		{
			return Ok(new ResumenRecorridoResponse
			{
				RecorridoId = recorrido.Id,
				TotalPuntos = 0,
				DistanciaTotalMetros = 0.0,
				DuracionSegundos = 0.0,
				VelocidadPromedioKmh = 0.0
			});
		}
		try
		{
			List<CoordenadaGps> coordenadas = JsonSerializer.Deserialize<List<CoordenadaGps>>(recorrido.Ruta_Coordenadas, new JsonSerializerOptions
			{
				PropertyNameCaseInsensitive = true
			}) ?? new List<CoordenadaGps>();
			return Ok(CalcularResumen(coordenadas, recorrido.Id));
		}
		catch (JsonException exception)
		{
			log.LogWarning(exception, "No se pudo deserializar Ruta_Coordenadas del recorrido {RecorridoId}", recorrido.Id);
			return BadRequest(new
			{
				error = "El formato de Ruta_Coordenadas no es válido."
			});
		}
	}

	private static ResumenRecorridoResponse CalcularResumen(IEnumerable<CoordenadaGps> coordenadas, int? recorridoId = null)
	{
		List<CoordenadaGps> list = coordenadas.ToList();
		var list2 = (from c in list
			where c.Latitud.HasValue && c.Longitud.HasValue
			select new
			{
				Latitud = (double)c.Latitud.Value,
				Longitud = (double)c.Longitud.Value,
				Timestamp = c.Timestamp
			}).ToList();
		if (list2.Count < 2)
		{
			return new ResumenRecorridoResponse
			{
				RecorridoId = recorridoId,
				TotalPuntos = list2.Count,
				DistanciaTotalMetros = 0.0,
				DuracionSegundos = 0.0,
				VelocidadPromedioKmh = 0.0,
				Coordenadas = list
			};
		}
		double num = 0.0;
		for (int num2 = 1; num2 < list2.Count; num2++)
		{
			num += GeoUtil.DistanciaMetros(list2[num2 - 1].Latitud, list2[num2 - 1].Longitud, list2[num2].Latitud, list2[num2].Longitud);
		}
		DateTime? dateTime = list2.FirstOrDefault(p => p.Timestamp.HasValue)?.Timestamp;
		DateTime? dateTime2 = list2.LastOrDefault(p => p.Timestamp.HasValue)?.Timestamp;
		double? num3 = null;
		if (dateTime.HasValue && dateTime2.HasValue && dateTime2.Value > dateTime.Value)
		{
			num3 = (dateTime2.Value - dateTime.Value).TotalSeconds;
		}
		double? num4 = null;
		if (num3.HasValue && num3.GetValueOrDefault() > 0.0 && num > 0.0)
		{
			num4 = num / 1000.0 / (num3.Value / 3600.0);
		}
		return new ResumenRecorridoResponse
		{
			RecorridoId = recorridoId,
			TotalPuntos = list2.Count,
			DistanciaTotalMetros = Math.Round(num, 2),
			DuracionSegundos = ((!num3.HasValue) ? ((double?)null) : new double?(Math.Round(num3.Value, 2))),
			VelocidadPromedioKmh = ((!num4.HasValue) ? ((double?)null) : new double?(Math.Round(num4.Value, 2))),
			Coordenadas = list
		};
	}

	[HttpGet("catalogos/discapacidades")]
	[ProducesResponseType(200)]
	public async Task<IActionResult> GetDiscapacidades(CancellationToken ct)
	{
		return Ok(await db.TiposDiscapacidad.Select((CatTipoDiscapacidad d) => new { d.Id, d.Nombre }).ToListAsync(ct));
	}

	[HttpGet("catalogos/eventos")]
	[ProducesResponseType(200)]
	public async Task<IActionResult> GetTiposEvento(CancellationToken ct)
	{
		return Ok(await db.TiposEvento.Select((CatTipoEvento e) => new { e.Id, e.NombreEvento, e.Severidad }).ToListAsync(ct));
	}
}
