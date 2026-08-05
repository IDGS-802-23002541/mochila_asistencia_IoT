using System;

namespace CangureraInteligente.DTOs;

public record RecorridoHistorialResponse
{
    public int Id { get; init; }
    public string DispositivoMac { get; init; } = string.Empty;
    public DateTime FechaInicio { get; init; }
    public DateTime? FechaFin { get; init; }
    public double DuracionSegundos { get; init; }
    public int TotalEventos { get; init; }
    public double DistanciaTotalMetros { get; init; }
}