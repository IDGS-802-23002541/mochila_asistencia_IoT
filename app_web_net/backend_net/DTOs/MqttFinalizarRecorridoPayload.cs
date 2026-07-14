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
	/// Array JSON de coordenadas GPS grabadas durante el recorrido, ya
	/// serializado como string por el ESP32.
	/// Formato: [{"lat":21.1234,"lon":-101.5678,"ts":"2025-06-25T10:00:00Z"}, ...]
	/// </summary>
	[JsonPropertyName("rutaCoordenadas")]
	public string RutaCoordenadas { get; init; } = "[]";

	/// <summary>
	/// AJUSTADO: timestamp del momento en que el usuario devolvió la mochila.
	/// Acepta epoch Unix en segundos/milisegundos (lo más probable según el
	/// firmware) o cadena ISO-8601, gracias a FlexibleUnixDateTimeConverter.
	/// Antes este campo esperaba forzosamente un string ISO-8601 y hubiera
	/// tronado al deserializar un número.
	/// </summary>
	[JsonPropertyName("fechaFin")]
	[JsonConverter(typeof(FlexibleUnixDateTimeConverter))]
	public DateTime FechaFin { get; init; } = DateTime.UtcNow;
}
