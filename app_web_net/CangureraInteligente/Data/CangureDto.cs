using System.ComponentModel.DataAnnotations;
using System.Text.Json;
using System.Text.Json.Serialization;

namespace CangureraInteligente.DTOs;

// ═══════════════════════════════════════════════════════════════════
//  HTTP  –  App Móvil → API
// ═══════════════════════════════════════════════════════════════════

/// <summary>
/// Body del POST /api/recorridos/iniciar enviado por la app móvil.
/// </summary>
public record IniciarRecorridoRequest
{
    /// <summary>MAC del ESP32 que se presta. Ej: "24:0A:C4:8B:58:FC"</summary>
    [Required, RegularExpression(@"^([0-9A-Fa-f]{2}:){5}[0-9A-Fa-f]{2}$",
        ErrorMessage = "Formato de MAC inválido. Esperado: XX:XX:XX:XX:XX:XX")]
    public string DispositivoMac { get; init; } = string.Empty;

    /// <summary>Edad del usuario (opcional).</summary>
    [Range(1, 120)]
    public int? UsuarioEdad { get; init; }

    /// <summary>ID de la discapacidad del catálogo (opcional).</summary>
    public int? DiscapacidadId { get; init; }
}

/// <summary>
/// Respuesta del POST /api/recorridos/iniciar.
/// La app móvil manda RecorridoId al ESP32 vía Bluetooth.
/// </summary>
public record IniciarRecorridoResponse
{
    public int RecorridoId { get; init; }
    public string DispositivoMac { get; init; } = string.Empty;
    public DateTime FechaInicio { get; init; }
    public string Mensaje { get; init; } = "Recorrido iniciado correctamente";
}

/// <summary>
/// Detalle de un recorrido (GET /api/recorridos/{id}).
/// </summary>
public record RecorridoDetalleResponse
{
    public int Id { get; init; }
    public string DispositivoMac { get; init; } = string.Empty;
    public string Organizacion { get; init; } = string.Empty;
    public DateTime FechaInicio { get; init; }
    public DateTime? FechaFin { get; init; }
    public int? UsuarioEdad { get; init; }
    public string? Discapacidad { get; init; }
    public bool Activo => FechaFin is null;
    public int TotalEventos { get; init; }
}

// ═══════════════════════════════════════════════════════════════════
//  MQTT  –  ESP32 → Broker → API
// ═══════════════════════════════════════════════════════════════════

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
    public bool GeoEsEstimado { get; init; } = false;

    /// <summary>Fuerza del impacto en G (solo eventos de caída). Null si no aplica.</summary>
    [JsonPropertyName("fuerzaImpactoG")]
    public decimal? FuerzaImpactoG { get; init; }
}

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

/// <summary>
/// Payload periódico de telemetría enviado por el ESP32.
/// Topic: cangurera/telemetria
/// </summary>
public record MqttTelemetryPayload
{
    [JsonPropertyName("dispositivoId")]
    public int DispositivoId { get; init; }

    [JsonPropertyName("latitud")]
    public decimal? Latitud { get; init; }

    [JsonPropertyName("longitud")]
    public decimal? Longitud { get; init; }

    [JsonPropertyName("velocidad")]
    public decimal? Velocidad { get; init; }

    [JsonPropertyName("bateria")]
    public int? Bateria { get; init; }

    [JsonPropertyName("fecha")]
    [JsonConverter(typeof(FlexibleUnixDateTimeConverter))]
    public DateTime Fecha { get; init; } = DateTime.UtcNow;
}

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
    private const long MillisecondsThreshold = 100_000_000_000; // ~año 5138 en segundos

    public override DateTime Read(ref Utf8JsonReader reader, Type typeToConvert, JsonSerializerOptions options)
    {
        if (reader.TokenType == JsonTokenType.Number)
        {
            return FromUnix(reader.GetInt64());
        }

        if (reader.TokenType == JsonTokenType.String)
        {
            var text = reader.GetString();

            if (long.TryParse(text, out var asLong))
                return FromUnix(asLong);

            if (DateTime.TryParse(text, System.Globalization.CultureInfo.InvariantCulture,
                    System.Globalization.DateTimeStyles.AdjustToUniversal | System.Globalization.DateTimeStyles.AssumeUniversal,
                    out var parsed))
            {
                return parsed;
            }
        }

        throw new JsonException($"No se pudo interpretar el valor de fecha/hora (token: {reader.TokenType}).");
    }

    public override void Write(Utf8JsonWriter writer, DateTime value, JsonSerializerOptions options)
    {
        writer.WriteNumberValue(new DateTimeOffset(DateTime.SpecifyKind(value, DateTimeKind.Utc)).ToUnixTimeSeconds());
    }

    private static DateTime FromUnix(long value) =>
        value >= MillisecondsThreshold
            ? DateTimeOffset.FromUnixTimeMilliseconds(value).UtcDateTime
            : DateTimeOffset.FromUnixTimeSeconds(value).UtcDateTime;
}