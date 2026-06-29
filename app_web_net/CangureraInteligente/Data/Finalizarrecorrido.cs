namespace CangureraInteligente.DTOs;

/// <summary>
/// Payload MQTT publicado por el ESP32 al finalizar un recorrido.
/// Topic: cangurera/recorrido/finalizar
/// </summary>
public class FinalizarRecorridoPayload
{
    /// <summary>Id del recorrido que se está cerrando.</summary>
    public int RecorridoId { get; set; }

    /// <summary>
    /// Momento de finalización en formato Unix timestamp
    /// (segundos transcurridos desde 1970-01-01 UTC, "epoch").
    /// </summary>
    public long FechaFin { get; set; }

    /// <summary>Coordenadas recolectadas durante el recorrido.</summary>
    public List<CoordenadaPayload> Coordenadas { get; set; } = new();
}

/// <summary>Punto de geolocalización individual dentro de un recorrido.</summary>
public class CoordenadaPayload
{
    public double Lat { get; set; }
    public double Lon { get; set; }

    /// <summary>Timestamp Unix (segundos) de este punto, si el ESP32 lo incluye.</summary>
    public long? Ts { get; set; }
}