using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;

namespace CangureraInteligente.Models;

[Table("Cat_TiposEvento", Schema = "Operativo")]
public class CatTipoEvento
{
	[Key]
	public int Id { get; set; }

	[Required]
	[MaxLength(50)]
	public string NombreEvento { get; set; } = string.Empty;

	[Required]
	[MaxLength(20)]
	public string Severidad { get; set; } = string.Empty;
}
