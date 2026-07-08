using System;
using System.Text.Json.Serialization;

namespace CangureraInteligente.DTOs;

/// <summary>
/// Payload periódico de telemetría enviado por el ESP32.
/// Topic: cangurera/telemetria
/// </summary>
public record MqttTelemetryPayload
{
	[JsonPropertyName("MacAddress")]
	public string MacAddress { get; init; } = string.Empty;

	[JsonPropertyName("latitud")]
	public decimal? Latitud { get; init; }

	[JsonPropertyName("longitud")]
	public decimal? Longitud { get; init; }

	[JsonPropertyName("fecha")]
	[JsonConverter(typeof(FlexibleUnixDateTimeConverter))]
	public DateTime Fecha { get; init; } = DateTime.UtcNow;
}
