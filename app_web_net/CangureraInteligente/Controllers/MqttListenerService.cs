using System.Text;
using System.Text.Json;
using CangureraInteligente.DTOs;
using CangureraInteligente.Services;
using Microsoft.Extensions.DependencyInjection;
using MQTTnet;
using MQTTnet.Client;
using MQTTnet.Protocol;

namespace CangureraInteligente.Services;

/// <summary>
/// Servicio en segundo plano que escucha el topic MQTT cangurera/telemetria.
/// </summary>
public class MqttListenerService : BackgroundService
{
    private const string TelemetryTopic = "cangurera/telemetria";

    private readonly IServiceScopeFactory _scopeFactory;
    private readonly ILogger<MqttListenerService> _log;
    private readonly MqttSettings _cfg;
    private IMqttClient? _client;

    public MqttListenerService(
        IServiceScopeFactory scopeFactory,
        ILogger<MqttListenerService> log,
        MqttSettings cfg)
    {
        _scopeFactory = scopeFactory;
        _log = log;
        _cfg = cfg;
    }

    protected override async Task ExecuteAsync(CancellationToken stoppingToken)
    {
        var factory = new MqttFactory();
        _client = factory.CreateMqttClient();

        _client.ConnectedAsync += async _ =>
        {
            _log.LogInformation("MQTT conectado a {Host}:{Port}", _cfg.Host, _cfg.Port);

            await _client.SubscribeAsync(new MqttTopicFilterBuilder()
                .WithTopic(TelemetryTopic)
                .WithAtLeastOnceQoS()
                .Build(), stoppingToken);

            _log.LogInformation("Suscripción MQTT activa: {Topic}", TelemetryTopic);
        };

        _client.DisconnectedAsync += async args =>
        {
            if (stoppingToken.IsCancellationRequested)
                return;

            _log.LogWarning("MQTT desconectado. Reintentando en 5 s… ({Reason})", args.ReasonString);
            await Task.Delay(TimeSpan.FromSeconds(5), stoppingToken);
            try
            {
                await ConnectAsync(stoppingToken);
            }
            catch (Exception ex)
            {
                _log.LogWarning(ex, "Reconexión MQTT fallida. Se reintentará nuevamente.");
            }
        };

        _client.ApplicationMessageReceivedAsync += HandleIncomingMessageAsync;

        var delay = TimeSpan.FromSeconds(2);
        while (!stoppingToken.IsCancellationRequested)
        {
            try
            {
                await ConnectAsync(stoppingToken);
                break;
            }
            catch (Exception ex) when (!stoppingToken.IsCancellationRequested)
            {
                _log.LogWarning(ex, "No se pudo conectar a MQTT. Reintentando en {Delay}s…", delay.TotalSeconds);
                await Task.Delay(delay, stoppingToken);
                delay = TimeSpan.FromSeconds(Math.Min(delay.TotalSeconds * 2, 30));
            }
        }

        await Task.Delay(Timeout.Infinite, stoppingToken);
    }

    private Task HandleIncomingMessageAsync(MqttApplicationMessageReceivedEventArgs args)
    {
        return ProcessMessageAsync(args);
    }

    private async Task ProcessMessageAsync(MqttApplicationMessageReceivedEventArgs args)
    {
        var topic = args.ApplicationMessage.Topic;
        var payload = Encoding.UTF8.GetString(args.ApplicationMessage.PayloadSegment);

        _log.LogDebug("MQTT recibido [{Topic}]: {Payload}", topic, payload);

        if (!string.Equals(topic, TelemetryTopic, StringComparison.OrdinalIgnoreCase))
        {
            _log.LogWarning("Topic MQTT no manejado: {Topic}", topic);
            return;
        }

        var telemetry = JsonSerializer.Deserialize<MqttTelemetryPayload>(payload,
            new JsonSerializerOptions { PropertyNameCaseInsensitive = true });

        if (telemetry is null)
        {
            _log.LogWarning("Payload de telemetría inválido: {Payload}", payload);
            return;
        }

        using var scope = _scopeFactory.CreateScope();
        var processor = scope.ServiceProvider.GetRequiredService<IMqttTelemetryProcessor>();

        var success = await processor.ProcessAsync(telemetry);
        if (!success)
        {
            _log.LogWarning("El mensaje MQTT fue recibido pero no se procesó correctamente.");
        }
    }

    private async Task ConnectAsync(CancellationToken ct)
    {
        var builder = new MqttClientOptionsBuilder()
            .WithClientId(string.IsNullOrWhiteSpace(_cfg.ClientId)
                ? $"CangureraInteligente-{Guid.NewGuid():N}"
                : _cfg.ClientId)
            .WithCleanSession();

        if (!string.IsNullOrWhiteSpace(_cfg.Username) && !string.IsNullOrWhiteSpace(_cfg.Password))
        {
            builder.WithCredentials(_cfg.Username, _cfg.Password);
        }

        if (_cfg.UseWebSocket)
        {
            var scheme = _cfg.UseTls ? "wss" : "ws";
            var wsUri = $"{scheme}://{_cfg.Host}:{_cfg.Port}/mqtt";
            _log.LogInformation("Conectando MQTT por WebSocket: {Uri}", wsUri);
            builder.WithWebSocketServer(wsUri);
        }
        else
        {
            _log.LogInformation("Conectando MQTT por TCP: {Host}:{Port}", _cfg.Host, _cfg.Port);
            builder.WithTcpServer(_cfg.Host, _cfg.Port);
            if (_cfg.UseTls)
            {
                builder.WithTls();
            }
        }

        var options = builder.Build();
        await _client!.ConnectAsync(options, ct);
    }

    public override async Task StopAsync(CancellationToken cancellationToken)
    {
        if (_client?.IsConnected == true)
        {
            await _client.DisconnectAsync(cancellationToken: cancellationToken);
        }

        await base.StopAsync(cancellationToken);
    }
}

/// <summary>
/// Configuración del broker MQTT (leída desde appsettings.json → sección "MQTT").
/// Soporta TCP directo y WebSocket en puertos 80/443.
/// </summary>
public class MqttSettings
{
    public string Host { get; set; } = "localhost";
    public int Port { get; set; } = 443;
    public string? Username { get; set; }
    public string? Password { get; set; }
    public string ClientId { get; set; } = string.Empty;
    public bool UseWebSocket { get; set; } = true;
    public bool UseTls { get; set; } = true;
}
