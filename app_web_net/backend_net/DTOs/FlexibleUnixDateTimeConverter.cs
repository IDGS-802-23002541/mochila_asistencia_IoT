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
/// </summary>
public class FlexibleUnixDateTimeConverter : JsonConverter<DateTime>
{
	private const long MillisecondsThreshold = 100000000000L;

	public override DateTime Read(ref Utf8JsonReader reader, Type typeToConvert, JsonSerializerOptions options)
	{
		if (reader.TokenType == JsonTokenType.Number)
		{
			return FromUnix(reader.GetInt64());
		}
		if (reader.TokenType == JsonTokenType.String)
		{
			string s = reader.GetString();
			if (long.TryParse(s, out var result))
			{
				return FromUnix(result);
			}
			if (DateTime.TryParse(s, CultureInfo.InvariantCulture, DateTimeStyles.AdjustToUniversal | DateTimeStyles.AssumeUniversal, out var result2))
			{
				return result2;
			}
		}
		throw new JsonException($"No se pudo interpretar el valor de fecha/hora (token: {reader.TokenType}).");
	}

	public override void Write(Utf8JsonWriter writer, DateTime value, JsonSerializerOptions options)
	{
		writer.WriteNumberValue(new DateTimeOffset(DateTime.SpecifyKind(value, DateTimeKind.Utc)).ToUnixTimeSeconds());
	}

	private static DateTime FromUnix(long value)
	{
		if (value < 100000000000L)
		{
			return DateTimeOffset.FromUnixTimeSeconds(value).UtcDateTime;
		}
		return DateTimeOffset.FromUnixTimeMilliseconds(value).UtcDateTime;
	}
}
