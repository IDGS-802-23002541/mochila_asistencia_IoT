using System;

namespace CangureraInteligente.DTOs;

/// <summary>
/// Detalle de un recorrido (GET /api/recorridos/{id}).
/// </summary>
public record RecorridoDetalleResponse
{
	public int Id { get; init; }

	public string DispositivoMac { get; init; } = string.Empty;

	public string Organizacion { get; init; } = string.Empty;

	public DateTime FechaInicio { get; init; }

	public DateTime? FechaFin { get; init; }

	public int? UsuarioEdad { get; init; }

	public string? Discapacidad { get; init; }

	public bool Activo => !FechaFin.HasValue;

	public int TotalEventos { get; init; }
}
