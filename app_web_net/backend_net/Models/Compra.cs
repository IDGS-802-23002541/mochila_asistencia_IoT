using System;
using System.Collections.Generic;
using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;

namespace CangureraInteligente.Models;

[Table("Compras", Schema = "Operativo")]
public class Compra
{
    [Key]
    public int IdCompra { get; set; }

    public DateTime FechaCompra { get; set; } = DateTime.Now;

    public int IdProveedor { get; set; }

    [Column(TypeName = "decimal(18,2)")]
    public decimal Total { get; set; }

    [ForeignKey(nameof(IdProveedor))]
    public Proveedor? Proveedor { get; set; }

    public ICollection<DetalleCompra> Detalles { get; set; }
}