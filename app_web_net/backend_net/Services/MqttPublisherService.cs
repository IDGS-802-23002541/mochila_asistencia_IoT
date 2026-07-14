using System.Text.Json;
using System.Threading;
using System.Threading.Tasks;
using CangureraInteligente.DTOs;
using MQTTnet;
using MQTTnet.Protocol;
using Microsoft.Extensions.Logging;

namespace CangureraInteligente.Services;

public class MqttPublisherService : IMqttPublisherService
{
	private const string TopicPull = "cangurera/pull";

	private readonly MqttConnectionManager _conn;

	private readonly ILogger<MqttPublisherService> _log;

	public MqttPublisherService(MqttConnectionManager conn, ILogger<MqttPublisherService> log)
	{
		_conn = conn;
		_log = log;
	}

	public async Task PublicarAlertaZonaCalienteAsync(ZonaCalienteAlertaPayload payload, CancellationToken ct = default(CancellationToken))
	{
		if (!_conn.IsConnected)
		{
			_log.LogWarning("No se publicó alerta de zona caliente: MQTT desconectado (dispositivo {Mac}).", payload.MacAddress);
			return;
		}
		string json = JsonSerializer.Serialize(payload);
		MqttApplicationMessage applicationMessage = new MqttApplicationMessageBuilder().WithTopic("cangurera/pull").WithPayload(json).WithQualityOfServiceLevel(MqttQualityOfServiceLevel.AtLeastOnce)
			.Build();
		await _conn.Client.PublishAsync(applicationMessage, ct);
		_log.LogInformation("Alerta de zona caliente publicada [{Topic}]: {Json}", "cangurera/pull", json);
	}
}
