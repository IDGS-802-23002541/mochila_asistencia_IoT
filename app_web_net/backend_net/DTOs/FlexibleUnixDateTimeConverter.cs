using System;
using System.Globalization;
using System.Text.Json;
using System.Text.Json.Serialization;

namespace CangureraInteligente.DTOs;

/// <summary>
/// NUEVO: convierte un timestamp enviado por el ESP32 a DateTime UTC. Acepta:
///   - epoch Unix en segundos (ej. 1719526529)
///   - epoch Unix en milisegundos (ej. 1719526529000)
///   - cadena ISO-8601 (ej. "2025-06-25T10:00:00Z")
/// El formato exacto que usa el firmware no está confirmado, así que se
/// detecta automáticamente: si el token es numérico, por su magnitud; si es
/// string, primero se intenta como número y luego como fecha ISO-8601.
/// Si el valor cae fuera del rango razonable (ej. epoch de 2000 enviado por
/// el ESP32) se deja pasar para que MqttTelemetryProcessor.SanitizeTimestamp
/// aplique el fallback a la hora del servidor; no se descarta el mensaje.
/// </summary>
public class FlexibleUnixDateTimeConverter : JsonConverter<DateTime>
{
	private const long MillisecondsThreshold = 100000000000L;
	private static readonly DateTime MinReasonableUtc = new DateTime(2020, 1, 1, 0, 0, 0, DateTimeKind.Utc);
	private static readonly DateTime MaxReasonableUtc = new DateTime(2100, 1, 1, 0, 0, 0, DateTimeKind.Utc);

	public override DateTime Read(ref Utf8JsonReader reader, Type typeToConvert, JsonSerializerOptions options)
	{
		if (reader.TokenType == JsonTokenType.Number)
		{
			return FromUnixStrict(reader.GetInt64());
		}
		if (reader.TokenType == JsonTokenType.String)
		{
			string text = reader.GetString()?.Trim() ?? string.Empty;
			if (long.TryParse(text, NumberStyles.Integer, CultureInfo.InvariantCulture, out var numericValue))
			{
				return FromUnixStrict(numericValue);
			}
			if (DateTimeOffset.TryParse(text, CultureInfo.InvariantCulture, DateTimeStyles.RoundtripKind | DateTimeStyles.AllowWhiteSpaces, out var parsedOffset))
			{
				return parsedOffset.UtcDateTime;
			}
		}
		throw new JsonException($"No se pudo interpretar el valor de fecha/hora (token: {reader.TokenType}).");
	}

	public override void Write(Utf8JsonWriter writer, DateTime value, JsonSerializerOptions options)
	{
		writer.WriteNumberValue(new DateTimeOffset(DateTime.SpecifyKind(value, DateTimeKind.Utc)).ToUnixTimeSeconds());
	}

	private static DateTime FromUnixStrict(long value)
	{
		// Valores <= 0 o fuera de rango se devuelven tal cual para que el
		// procesador aplique el fallback a DateTime.UtcNow. Nunca lanzamos
		// aquí: lanzar descartaría el mensaje MQTT completo en el listener.
		if (Math.Abs(value) < MillisecondsThreshold)
		{
			return DateTimeOffset.FromUnixTimeSeconds(value).UtcDateTime;
		}
		return DateTimeOffset.FromUnixTimeMilliseconds(value).UtcDateTime;
	}
}
