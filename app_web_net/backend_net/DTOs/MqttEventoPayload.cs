using System;
using System.Text.Json.Serialization;

namespace CangureraInteligente.DTOs;

/// <summary>
/// Payload publicado por el ESP32 cuando detecta un evento.
/// Topic: cangurera/eventos
/// </summary>
public record MqttEventoPayload
{
	/// <summary>ID recibido del móvil vía Bluetooth.</summary>
	[JsonPropertyName("recorridoId")]
	public int RecorridoId { get; init; }

	/// <summary>ID del catálogo Cat_TiposEvento.</summary>
	[JsonPropertyName("tipoEventoId")]
	public int TipoEventoId { get; init; }

	/// <summary>
	/// NUEVO: timestamp del evento. Acepta epoch Unix en segundos o
	/// milisegundos, o una cadena ISO-8601 (ver FlexibleUnixDateTimeConverter
	/// más abajo). Si el ESP32 no lo manda, se usa la hora del servidor.
	/// </summary>
	[JsonPropertyName("timestamp")]
	[JsonConverter(typeof(FlexibleUnixDateTimeConverter))]
	public DateTime? Timestamp { get; init; }

	/// <summary>Latitud GPS. Null si no hay señal.</summary>
	[JsonPropertyName("latitud")]
	public decimal? Latitud { get; init; }

	/// <summary>Longitud GPS. Null si no hay señal.</summary>
	[JsonPropertyName("longitud")]
	public decimal? Longitud { get; init; }

	/// <summary>true = coordenadas estimadas (GPS sin fix).</summary>
	[JsonPropertyName("geoEsEstimado")]
	public bool GeoEsEstimado { get; init; }

	/// <summary>Fuerza del impacto en G (solo eventos de caída). Null si no aplica.</summary>
	[JsonPropertyName("fuerzaImpactoG")]
	public decimal? FuerzaImpactoG { get; init; }

	[JsonPropertyName("ir_izq")]
	public bool? IrIzquierdo { get; init; }

	[JsonPropertyName("ir_der")]
	public bool? IrDerecho { get; init; }

	[JsonPropertyName("dist")]
	public decimal? Dist { get; init; }
}
