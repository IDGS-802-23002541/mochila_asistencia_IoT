using System.Collections.Generic;

namespace CangureraInteligente.DTOs;

public record ResumenRecorridoResponse
{
	public int? RecorridoId { get; init; }

	public int TotalPuntos { get; init; }

	public double DistanciaTotalMetros { get; init; }

	public double? DuracionSegundos { get; init; }

	public double? VelocidadPromedioKmh { get; init; }

	public List<CoordenadaGps> Coordenadas { get; init; } = new List<CoordenadaGps>();
}
