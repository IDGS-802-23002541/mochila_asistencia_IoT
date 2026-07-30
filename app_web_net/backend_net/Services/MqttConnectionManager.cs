using System;
using System.Threading;
using System.Threading.Tasks;
using CangureraInteligente.Models;
using MQTTnet;
using MQTTnet.Client;
using Microsoft.Extensions.Logging;
using System.Net.Security;
using System.Linq;                                  // para el .All(...)
using System.Security.Cryptography.X509Certificates; // para X509ChainStatusFlags

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
				mqttClientOptionsBuilder.WithTlsOptions(o =>
				{
					o.UseTls();
					o.WithCertificateValidationHandler(context =>
{
	// Solo permitimos el caso específico de "no se pudo verificar revocación",
	// que es común quntdo el cliente no puede alcanzar el servidor OCSP/CRL.
	// Cualquier otro error (nombre incorrecto, certificado expirado, cadena rota) se rechaza.
	if (context.SslPolicyErrors == SslPolicyErrors.None)
	{
		return true;
	}

	if (context.SslPolicyErrors == SslPolicyErrors.RemoteCertificateChainErrors
		&& context.Chain != null
		&& context.Chain.ChainStatus.All(s => s.Status == X509ChainStatusFlags.RevocationStatusUnknown
											  || s.Status == X509ChainStatusFlags.OfflineRevocation))
	{
		_log.LogWarning("Aceptando certificado MQTT: no se pudo verificar el estado de revocación (offline/OCSP inalcanzable).");
		return true;
	}

	_log.LogError("Certificado MQTT rechazado: {Errors}", context.SslPolicyErrors);
	return false;
});

				});
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
