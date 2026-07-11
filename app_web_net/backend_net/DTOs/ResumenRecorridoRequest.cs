using System.Collections.Generic;

namespace CangureraInteligente.DTOs;

public record ResumenRecorridoRequest
{
	public int? RecorridoId { get; init; }

	public List<CoordenadaGps> Coordenadas { get; init; } = new List<CoordenadaGps>();
}
