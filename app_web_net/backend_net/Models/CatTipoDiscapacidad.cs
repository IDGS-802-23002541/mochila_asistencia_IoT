using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;

namespace CangureraInteligente.Models;

[Table("Cat_TiposDiscapacidad", Schema = "Operativo")]
public class CatTipoDiscapacidad
{
	[Key]
	public int Id { get; set; }

	[Required]
	[MaxLength(50)]
	public string Nombre { get; set; } = string.Empty;
}
