using System.Threading;
using System.Threading.Tasks;
using CangureraInteligente.DTOs;

namespace CangureraInteligente.Services;

public interface IMqttPublisherService
{
	Task PublicarAlertaZonaCalienteAsync(ZonaCalienteAlertaPayload payload, CancellationToken ct = default(CancellationToken));
}
