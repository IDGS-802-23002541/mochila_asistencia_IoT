using CangureraInteligente.DTOs;

namespace CangureraInteligente.Services;

public interface IMqttPublisherService
{
    Task PublicarAlertaZonaCalienteAsync(ZonaCalienteAlertaPayload payload, CancellationToken ct = default);
}