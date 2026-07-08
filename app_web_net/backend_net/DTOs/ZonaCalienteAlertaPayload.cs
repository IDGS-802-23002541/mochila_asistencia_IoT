using System.Text.Json.Serialization;

namespace CangureraInteligente.DTOs;

public record ZonaCalienteAlertaPayload
{
	[JsonPropertyName("MacAdress")]
	public string MacAddress { get; init; } = string.Empty;

	[JsonPropertyName("mensaje")]
	public string Mensaje { get; init; } = "acercandose_zona_caliente";

	[JsonPropertyName("tipoEventoid")]
	public int TipoEventoId { get; init; }

	[JsonPropertyName("latitud")]
	public decimal Latitud { get; init; }

	[JsonPropertyName("longitud")]
	public decimal Longitud { get; init; }

	[JsonPropertyName("distanciaMetros")]
	public double DistanciaMetros { get; init; }
}
