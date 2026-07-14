using System;
using System.Text.Json.Serialization;

namespace CangureraInteligente.DTOs;

/// <summary>
/// Payload publicado por el ESP32 al terminar el recorrido.
/// Topic: cangurera/recorrido/finalizar
/// </summary>
public record MqttFinalizarRecorridoPayload
{
	/// <summary>ID del recorrido activo.</summary>
	[JsonPropertyName("recorridoId")]
	public int RecorridoId { get; init; }

	/// <summary>
	/// Timestamp del momento en que el usuario devolvió la mochila.
	/// Acepta epoch Unix en segundos/milisegundos o cadena ISO-8601.
	/// </summary>
	[JsonPropertyName("fechaFin")]
	[JsonConverter(typeof(FlexibleUnixDateTimeConverter))]
	public DateTime FechaFin { get; init; } = DateTime.UtcNow;
}
