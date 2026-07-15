using System;
using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;
using System.Text.Json.Serialization;

namespace CangureraInteligente.Models;

[Table("RecorridoCoordenadas", Schema = "Operativo")]
public class RecorridoCoordenada
{
	[Key]
	public int Id { get; set; }

	public int RecorridoId { get; set; }

	public DateTime Fecha { get; set; }

	public decimal Latitud { get; set; }

	public decimal Longitud { get; set; }

	[ForeignKey("RecorridoId")]
	[JsonIgnore]
	public Recorrido Recorrido { get; set; }
}
