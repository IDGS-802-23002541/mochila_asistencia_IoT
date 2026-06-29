namespace CangureraInteligente.DTOs;

/// <summary>
/// Payload MQTT publicado por el ESP32 al registrar un evento durante el recorrido
/// (caída, impacto, botón de pánico, etc.).
/// Topic: cangurera/recorrido/evento
/// </summary>
public class RegistrarEventoPayload
{
    /// <summary>Id del recorrido al que pertenece el evento.</summary>
    public int RecorridoId { get; set; }

    /// <summary>Id del tipo de evento (catálogo TiposEvento).</summary>
    public int TipoEventoId { get; set; }

    /// <summary>
    /// Timestamp del evento. El firmware no confirma si envía segundos o
    /// milisegundos desde epoch Unix; se normaliza automáticamente en el
    /// processor según la magnitud del número (ver <c>UnixTimeUtil</c>).
    /// </summary>
    public long Timestamp { get; set; }

    public double Latitud { get; set; }
    public double Longitud { get; set; }

    /// <summary>true si la posición es estimada; false si viene de GPS real.</summary>
    public bool GeoEstimado { get; set; }

    /// <summary>Fuerza de impacto registrada por el acelerómetro, en G's.</summary>
    public double FuerzaImpactoG { get; set; }
}