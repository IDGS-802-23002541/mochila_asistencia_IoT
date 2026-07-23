using System;
using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;
using System.Text.Json.Serialization;

namespace CangureraInteligente.Models;

[Table("Usuarios", Schema = "Operativo")]
public class Usuario
{
	[Key]
	public int Id { get; set; }

	public int OrganizacionId { get; set; }

	[Required]
	[MaxLength(150)]
	public string Nombre { get; set; } = string.Empty;

	[Required]
	[MaxLength(150)]
	public string Correo { get; set; } = string.Empty;

	[Required]
	[MaxLength(255)]
	public string Contrasena_Hash { get; set; } = string.Empty;

	[Required]
	[MaxLength(20)]
	public string Rol { get; set; } = "usuario";

	public DateTime FechaRegistro { get; set; } = DateTime.UtcNow;

	public bool Estado_Activo { get; set; } = true;

	[ForeignKey("OrganizacionId")]
	[JsonIgnore]
	public Organizacion Organizacion { get; set; }
}
