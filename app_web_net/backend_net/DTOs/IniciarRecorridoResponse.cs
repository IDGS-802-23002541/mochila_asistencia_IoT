using System;

namespace CangureraInteligente.DTOs;

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
