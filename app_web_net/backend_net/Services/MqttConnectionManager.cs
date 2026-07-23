using System;
using System.Threading;
using System.Threading.Tasks;
using CangureraInteligente.Models;
using MQTTnet;
using MQTTnet.Client;
using Microsoft.Extensions.Logging;

namespace CangureraInteligente.Services;

public class MqttConnectionManager : IAsyncDisposable
{
	private readonly ILogger<MqttConnectionManager> _log;

	private readonly MqttSettings _cfg;

	public IMqttClient Client { get; }

	public bool IsConnected => Client.IsConnected;

	public MqttConnectionManager(ILogger<MqttConnectionManager> log, MqttSettings cfg)
	{
		_log = log;
		_cfg = cfg;
		Client = new MqttFactory().CreateMqttClient();
	}

	public async Task ConnectAsync(CancellationToken ct)
	{
		MqttClientOptionsBuilder mqttClientOptionsBuilder = new MqttClientOptionsBuilder().WithClientId(string.IsNullOrWhiteSpace(_cfg.ClientId) ? $"CangureraInteligente-{Guid.NewGuid():N}" : _cfg.ClientId).WithCleanSession();
		if (!string.IsNullOrWhiteSpace(_cfg.Username) && !string.IsNullOrWhiteSpace(_cfg.Password))
		{
			mqttClientOptionsBuilder.WithCredentials(_cfg.Username, _cfg.Password);
		}
		if (_cfg.UseWebSocket)
		{
			string value = (_cfg.UseTls ? "wss" : "ws");
			string text = $"{value}://{_cfg.Host}:{_cfg.Port}/mqtt";
			_log.LogInformation("Conectando MQTT por WebSocket: {Uri}", text);
			mqttClientOptionsBuilder.WithWebSocketServer(text);
		}
		else
		{
			_log.LogInformation("Conectando MQTT por TCP: {Host}:{Port}", _cfg.Host, _cfg.Port);
			mqttClientOptionsBuilder.WithTcpServer(_cfg.Host, _cfg.Port);
			if (_cfg.UseTls)
			{
				mqttClientOptionsBuilder.WithTls();
			}
		}
		await Client.ConnectAsync(mqttClientOptionsBuilder.Build(), ct);
	}

	public async Task DisconnectAsync(CancellationToken ct = default(CancellationToken))
	{
		if (Client.IsConnected)
		{
			await Client.DisconnectAsync(MqttClientDisconnectOptionsReason.NormalDisconnection, null, 0u, null, ct);
		}
	}

	public async ValueTask DisposeAsync()
	{
		await DisconnectAsync();
		Client.Dispose();
	}
}
