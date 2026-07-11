using System;
using System.Collections.Generic;
using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;
using System.Text.Json.Serialization;

namespace CangureraInteligente.Models;

[Table("Organizaciones", Schema = "Operativo")]
public class Organizacion
{
	[Key]
	public int Id { get; set; }

	[Required]
	[MaxLength(150)]
	public string Nombre { get; set; } = string.Empty;

	[Required]
	[MaxLength(50)]
	public string Sector { get; set; } = string.Empty;

	[MaxLength(100)]
	public string? Contacto_Principal { get; set; }

	[MaxLength(100)]
	public string? Email_Contacto { get; set; }

	public DateTime FechaCreacion { get; set; } = DateTime.UtcNow;

	public bool Estado_Activo { get; set; } = true;

	[MaxLength(255)]
	public string? Contrasena_Hash { get; set; }

	[Required]
	[MaxLength(20)]
	public string Rol { get; set; } = "usuario";

	public bool Es_Interna { get; set; }

	[JsonIgnore]
	public ICollection<Dispositivo> Dispositivos { get; set; } = new List<Dispositivo>();

	[JsonIgnore]
	public ICollection<Usuario> Usuarios { get; set; } = new List<Usuario>();
}
