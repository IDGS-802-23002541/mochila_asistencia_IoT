using System;

namespace CangureraInteligente.DTOs;

public record EventoRecorridoResponse
{
    public string Tipo { get; init; } = string.Empty;
    public string Severidad { get; init; } = string.Empty;
    public DateTime Timestamp { get; init; }
}