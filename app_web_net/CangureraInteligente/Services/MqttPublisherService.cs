using System.Text.Json;
using CangureraInteligente.DTOs;
using MQTTnet;
using MQTTnet.Protocol;

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

    public async Task PublicarAlertaZonaCalienteAsync(ZonaCalienteAlertaPayload payload, CancellationToken ct = default)
    {
        if (!_conn.IsConnected)
        {
            _log.LogWarning("No se publicó alerta de zona caliente: MQTT desconectado (dispositivo {Id}).", payload.DispositivoId);
            return;
        }

        var json = JsonSerializer.Serialize(payload);

        var msg = new MqttApplicationMessageBuilder()
            .WithTopic(TopicPull)
            .WithPayload(json)
            .WithQualityOfServiceLevel(MqttQualityOfServiceLevel.AtLeastOnce)
            .Build();

        await _conn.Client.PublishAsync(msg, ct);

        _log.LogInformation("Alerta de zona caliente publicada [{Topic}]: {Json}", TopicPull, json);
    }
}