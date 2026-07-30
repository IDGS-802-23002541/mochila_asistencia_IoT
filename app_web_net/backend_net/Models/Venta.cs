using System;
using System.Collections.Generic;
using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;


namespace CangureraInteligente.Models;

[Table("Ventas", Schema = "Operativo")]
public class Venta
{
    [Key]
    public int IdVenta { get; set; }

    public DateTime FechaVenta { get; set; }

    [Column(TypeName = "decimal(18,2)")]
    public decimal Total { get; set; }

    public ICollection<DetalleVenta>? Detalles { get; set; }
}