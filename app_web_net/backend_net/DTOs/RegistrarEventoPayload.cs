namespace CangureraInteligente.DTOs;

/// <summary>
/// Payload MQTT publicado por el ESP32 al registrar un evento durante el recorrido
/// (caída, impacto, botón de pánico, etc.).
/// Topic: cangurera/recorrido/evento
/// </summary>
public record RegistrarEventoPayload : MqttEventoPayload;
