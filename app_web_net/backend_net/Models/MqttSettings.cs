namespace CangureraInteligente.Models;

/// <summary>
/// Configuración del broker MQTT (se lee desde appsettings.json en la sección "MQTT" o "Mqtt").
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
