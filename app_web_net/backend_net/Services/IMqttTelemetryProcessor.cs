using System.Threading;
using System.Threading.Tasks;
using CangureraInteligente.DTOs;

namespace CangureraInteligente.Services;

/// <summary>
/// Procesador de los mensajes MQTT enviados por el ESP32. Cada topic tiene su
/// propio método porque cada uno representa un caso de negocio distinto.
/// </summary>
public interface IMqttTelemetryProcessor
{
	/// <summary>Procesa telemetría periódica (topic cangurera/telemetria).</summary>
	Task<bool> ProcesarTelemetriaAsync(MqttTelemetryPayload payload, CancellationToken ct = default(CancellationToken));

	/// <summary>Procesa el registro de un evento puntual (topic cangurera/eventos).</summary>
	Task<bool> RegistrarEventoAsync(MqttEventoPayload payload, CancellationToken ct = default(CancellationToken));

	/// <summary>Procesa el cierre de un recorrido (topic cangurera/recorrido/finalizar).</summary>
	Task<bool> FinalizarRecorridoAsync(MqttFinalizarRecorridoPayload payload, CancellationToken ct = default(CancellationToken));
}
