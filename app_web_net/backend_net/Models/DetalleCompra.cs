using System;
using System.Collections.Generic;
using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;

namespace CangureraInteligente.Models;

[Table("DetalleCompra", Schema = "Operativo")]
public class DetalleCompra
{
    [Key]
    public int IdDetalleCompra { get; set; }

    public int IdCompra { get; set; }

    public int IdMateriaPrima { get; set; }

    public int Cantidad { get; set; }

    [Column(TypeName = "decimal(18,2)")]
    public decimal PrecioUnitario { get; set; }

    [ForeignKey(nameof(IdCompra))]
    public Compra? Compra { get; set; }

    [ForeignKey(nameof(IdMateriaPrima))]
    public MateriaPrima? MateriaPrima { get; set; }
}