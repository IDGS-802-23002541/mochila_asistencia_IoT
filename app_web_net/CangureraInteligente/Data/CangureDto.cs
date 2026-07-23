using System.ComponentModel.DataAnnotations;
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
    /// Array JSON de coordenadas GPS grabadas durante el recorrido.
    /// Formato: [{"lat":21.1234,"lon":-101.5678,"ts":"2025-06-25T10:00:00Z"}, ...]
    /// </summary>
    [JsonPropertyName("rutaCoordenadas")]
    public string RutaCoordenadas { get; init; } = "[]";

    /// <summary>Timestamp UTC del momento en que el usuario devolvió la mochila.</summary>
    [JsonPropertyName("fechaFin")]
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
    public DateTime Fecha { get; init; } = DateTime.UtcNow;
}