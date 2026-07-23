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

	public int? Usuario_Edad { get; set; }

	public int? DiscapacidadId { get; set; }

	public string? Ruta_Coordenadas { get; set; }

	[ForeignKey("DispositivoId")]
	[JsonIgnore]
	public Dispositivo Dispositivo { get; set; }

	[ForeignKey("DiscapacidadId")]
	public CatTipoDiscapacidad? Discapacidad { get; set; }

	[JsonIgnore]
	public ICollection<EventoDetectado> Eventos { get; set; } = new List<EventoDetectado>();
}
