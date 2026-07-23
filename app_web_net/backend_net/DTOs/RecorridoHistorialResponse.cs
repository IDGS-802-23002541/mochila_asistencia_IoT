using System;
using System.Text.Json.Serialization;

namespace CangureraInteligente.DTOs;

public record RecorridoHistorialResponse
{
	[JsonPropertyName("id")]
	public int Id { get; init; }

	[JsonPropertyName("dispositivoMac")]
	public string DispositivoMac { get; init; } = string.Empty;

	[JsonPropertyName("fechaInicio")]
	public DateTime FechaInicio { get; init; }

	[JsonPropertyName("fechaFin")]
	public DateTime? FechaFin { get; init; }

	[JsonPropertyName("duracionSegundos")]
	public double DuracionSegundos { get; init; }

	[JsonPropertyName("totalEventos")]
	public int TotalEventos { get; init; }

	[JsonPropertyName("distanciaTotalMetros")]
	public double DistanciaTotalMetros { get; init; }
}
