using System;
using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;
using System.Text.Json.Serialization;

namespace CangureraInteligente.Models;

[Table("Eventos_Detectados", Schema = "Operativo")]
public class EventoDetectado
{
	[Key]
	public long Id { get; set; }

	public int RecorridoId { get; set; }

	public int TipoEventoId { get; set; }

	public DateTime TimestampEvento { get; set; } = DateTime.UtcNow;

	[Column(TypeName = "decimal(10,8)")]
	public decimal? Latitud { get; set; }

	[Column(TypeName = "decimal(10,8)")]
	public decimal? Longitud { get; set; }

	public bool Geo_Es_Estimado { get; set; }

	[Column(TypeName = "decimal(5,2)")]
	public decimal? FuerzaImpactoG { get; set; }

	public bool? IrIzquierdo { get; set; }

	public bool? IrDerecho { get; set; }

	[Column(TypeName = "decimal(7,2)")]
	public decimal? DistanciaCm { get; set; }

	[ForeignKey("RecorridoId")]
	[JsonIgnore]
	public Recorrido Recorrido { get; set; }

	[ForeignKey("TipoEventoId")]
	public CatTipoEvento TipoEvento { get; set; }
}
