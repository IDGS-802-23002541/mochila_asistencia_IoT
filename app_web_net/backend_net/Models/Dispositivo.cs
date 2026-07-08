using System;
using System.Collections.Generic;
using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;

namespace CangureraInteligente.Models;

[Table("Dispositivos", Schema = "Operativo")]
public class Dispositivo
{
	[Key]
	public int Id { get; set; }

	public int OrganizacionId { get; set; }

	[Required]
	[MaxLength(17)]
	public string MacAddress { get; set; } = string.Empty;

	public DateTime FechaRegistro { get; set; } = DateTime.UtcNow;

	public DateTime? UltimaConexion { get; set; }

	[MaxLength(20)]
	public string Estado { get; set; } = "Activo";

	[ForeignKey("OrganizacionId")]
	public Organizacion Organizacion { get; set; }

	public ICollection<Recorrido> Recorridos { get; set; } = new List<Recorrido>();
}
