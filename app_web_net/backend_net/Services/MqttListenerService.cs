using System;
using System.Text;
using System.Text.Json;
using System.Threading;
using System.Threading.Tasks;
using CangureraInteligente.DTOs;
using CangureraInteligente.Models;
using MQTTnet;
using MQTTnet.Client;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Hosting;
using Microsoft.Extensions.Logging;

namespace CangureraInteligente.Services;

/// <summary>
/// Servicio en segundo plano que escucha los topics MQTT publicados por el ESP32:
///   - cangurera/telemetria           : telemetría periódica (heartbeat / última conexión).
///   - cangurera/eventos              : registro de un evento puntual (caída, impacto, etc.).
///   - cangurera/recorrido/finalizar  : cierre de un recorrido + ruta de coordenadas.
/// </summary>
public class MqttListenerService : BackgroundService
{
	private const string TopicTelemetria = "cangurera/telemetria";

	private const string TopicEventos = "cangurera/eventos";

	private const string TopicFinalizar = "cangurera/recorrido/finalizar";

	private static readonly JsonSerializerOptions JsonOpts = new JsonSerializerOptions
	{
		PropertyNameCaseInsensitive = true
	};

	private readonly IServiceScopeFactory _scopeFactory;

	private readonly ILogger<MqttListenerService> _log;

	private readonly MqttConnectionManager _conn;

	private readonly MqttSettings _cfg;

	private IMqttClient? _client;

	public MqttListenerService(IServiceScopeFactory scopeFactory, ILogger<MqttListenerService> log, MqttConnectionManager conn, MqttSettings cfg)
	{
		_scopeFactory = scopeFactory;
		_log = log;
		_conn = conn;
		_cfg = cfg;
	}

	protected override async Task ExecuteAsync(CancellationToken stoppingToken)
	{
		_client = _conn.Client;
		_client.ConnectedAsync += async delegate
		{
			_log.LogInformation("MQTT conectado a {Host}:{Port}", _cfg.Host, _cfg.Port);
			string[] array = new string[3] { "cangurera/telemetria", "cangurera/eventos", "cangurera/recorrido/finalizar" };
			foreach (string topic in array)
			{
				await _client.SubscribeAsync(new MqttTopicFilterBuilder().WithTopic(topic).WithAtLeastOnceQoS().Build(), stoppingToken);
			}
			_log.LogInformation("Suscripción MQTT activa: {T1}, {T2}, {T3}", "cangurera/telemetria", "cangurera/eventos", "cangurera/recorrido/finalizar");
		};
		_client.DisconnectedAsync += async delegate(MqttClientDisconnectedEventArgs args)
		{
			if (stoppingToken.IsCancellationRequested)
			{
				return;
			}
			_log.LogWarning("MQTT desconectado. Reintentando en 5 s… ({Reason})", args.ReasonString);
			await Task.Delay(TimeSpan.FromSeconds(5.0), stoppingToken);
			try
			{
				await ConnectAsync(stoppingToken);
			}
			catch (Exception exception2)
			{
				_log.LogWarning(exception2, "Reconexión MQTT fallida. Se reintentará nuevamente.");
			}
		};
		_client.ApplicationMessageReceivedAsync += HandleIncomingMessageAsync;
		TimeSpan delay = TimeSpan.FromSeconds(2.0);
		while (!stoppingToken.IsCancellationRequested)
		{
			try
			{
				await ConnectAsync(stoppingToken);
			}
			catch (Exception exception) when (!stoppingToken.IsCancellationRequested)
			{
				_log.LogWarning(exception, "No se pudo conectar a MQTT. Reintentando en {Delay}s…", delay.TotalSeconds);
				await Task.Delay(delay, stoppingToken);
				delay = TimeSpan.FromSeconds(Math.Min(delay.TotalSeconds * 2.0, 30.0));
				continue;
			}
			break;
		}
		await Task.Delay(-1, stoppingToken);
	}

	private Task HandleIncomingMessageAsync(MqttApplicationMessageReceivedEventArgs args)
	{
		return ProcessMessageAsync(args);
	}

	private async Task ProcessMessageAsync(MqttApplicationMessageReceivedEventArgs args)
	{
		string topic = args.ApplicationMessage.Topic;
		string payload = Encoding.UTF8.GetString(args.ApplicationMessage.PayloadSegment);
		_log.LogDebug("MQTT recibido [{Topic}]: {Payload}", topic, payload);
		using IServiceScope scope = _scopeFactory.CreateScope();
		IMqttTelemetryProcessor requiredService = scope.ServiceProvider.GetRequiredService<IMqttTelemetryProcessor>();
		bool flag;
		try
		{
			switch (topic)
			{
			case "cangurera/telemetria":
			{
				MqttTelemetryPayload mqttTelemetryPayload = JsonSerializer.Deserialize<MqttTelemetryPayload>(payload, JsonOpts);
				if ((object)mqttTelemetryPayload == null)
				{
					_log.LogWarning("Payload de telemetría inválido: {Payload}", payload);
					return;
				}
				flag = await requiredService.ProcesarTelemetriaAsync(mqttTelemetryPayload);
				break;
			}
			case "cangurera/eventos":
			{
				MqttEventoPayload mqttEventoPayload = JsonSerializer.Deserialize<MqttEventoPayload>(payload, JsonOpts);
				if ((object)mqttEventoPayload == null)
				{
					_log.LogWarning("Payload de evento inválido: {Payload}", payload);
					return;
				}
				flag = await requiredService.RegistrarEventoAsync(mqttEventoPayload);
				break;
			}
			case "cangurera/recorrido/finalizar":
			{
				MqttFinalizarRecorridoPayload mqttFinalizarRecorridoPayload = JsonSerializer.Deserialize<MqttFinalizarRecorridoPayload>(payload, JsonOpts);
				if ((object)mqttFinalizarRecorridoPayload == null)
				{
					_log.LogWarning("Payload de finalización inválido: {Payload}", payload);
					return;
				}
				flag = await requiredService.FinalizarRecorridoAsync(mqttFinalizarRecorridoPayload);
				break;
			}
			default:
				_log.LogWarning("Topic MQTT no manejado: {Topic}", topic);
				return;
			}
		}
		catch (JsonException exception)
		{
			_log.LogWarning(exception, "No se pudo deserializar el payload MQTT [{Topic}]: {Payload}", topic, payload);
			return;
		}
		if (!flag)
		{
			_log.LogWarning("El mensaje MQTT [{Topic}] fue recibido pero no se procesó correctamente.", topic);
		}
	}

	private Task ConnectAsync(CancellationToken ct)
	{
		_log.LogInformation("Conectando MQTT usando MqttConnectionManager.");
		return _conn.ConnectAsync(ct);
	}

	public override async Task StopAsync(CancellationToken cancellationToken)
	{
		await _conn.DisconnectAsync(cancellationToken);
		await base.StopAsync(cancellationToken);
	}
}
