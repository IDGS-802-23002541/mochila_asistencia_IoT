using System;
using System.Collections.Generic;
using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;
using System.Text.Json.Serialization;

namespace CangureraInteligente.Models;

[Table("Recorridos", Schema = "Operativo")]
public class Recorrido
{
	[Key]
	public int Id { get; set; }

	public int DispositivoId { get; set; }

	public DateTime FechaInicio { get; set; } = DateTime.UtcNow;

	public DateTime? FechaFin { get; set; }

	[ForeignKey("DispositivoId")]
	[JsonIgnore]
	public Dispositivo Dispositivo { get; set; }

	[JsonIgnore]
	public ICollection<EventoDetectado> Eventos { get; set; } = new List<EventoDetectado>();

	[JsonIgnore]
	public ICollection<RecorridoCoordenada> Coordenadas { get; set; } = new List<RecorridoCoordenada>();
}
