using System.Threading;
using System.Threading.Tasks;
using CangureraInteligente.DTOs;

namespace CangureraInteligente.Services;

/// <summary>
/// Procesador de mensajes de telemetría recibidos por MQTT.
/// Implementaciones deben reutilizar la lógica de negocio existente
/// (servicios/patrones de la aplicación) y no acceder directamente al DbContext.
/// </summary>
public interface IMqttTelemetryProcessor
{
    Task<bool> ProcessAsync(MqttTelemetryPayload payload, CancellationToken ct = default);
}
