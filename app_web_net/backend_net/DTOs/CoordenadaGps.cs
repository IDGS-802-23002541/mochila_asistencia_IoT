using System;
using System.Text.Json.Serialization;

namespace CangureraInteligente.DTOs;

public record CoordenadaGps
{
	[JsonPropertyName("lat")]
	public decimal? Latitud { get; init; }

	[JsonPropertyName("lon")]
	public decimal? Longitud { get; init; }

	[JsonPropertyName("ts")]
	[JsonConverter(typeof(FlexibleUnixDateTimeConverter))]
	public DateTime? Timestamp { get; init; }
}
