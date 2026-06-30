using MQTTnet;
using MQTTnet.Client;

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
        var builder = new MqttClientOptionsBuilder()
            .WithClientId(string.IsNullOrWhiteSpace(_cfg.ClientId)
                ? $"CangureraInteligente-{Guid.NewGuid():N}"
                : _cfg.ClientId)
            .WithCleanSession();

        if (!string.IsNullOrWhiteSpace(_cfg.Username) && !string.IsNullOrWhiteSpace(_cfg.Password))
            builder.WithCredentials(_cfg.Username, _cfg.Password);

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
            if (_cfg.UseTls) builder.WithTls();
        }

        await Client.ConnectAsync(builder.Build(), ct);
    }

    public async Task DisconnectAsync(CancellationToken ct = default)
    {
        if (Client.IsConnected)
            await Client.DisconnectAsync(cancellationToken: ct);
    }

    public async ValueTask DisposeAsync()
    {
        await DisconnectAsync();
        Client.Dispose();
    }
}