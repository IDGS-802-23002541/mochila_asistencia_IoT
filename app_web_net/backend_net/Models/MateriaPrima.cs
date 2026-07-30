using System;
using System.Collections.Generic;
using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;

namespace CangureraInteligente.Models;

[Table("MateriaPrima", Schema = "Operativo")]
public class MateriaPrima
{
    [Key]
    public int IdMateriaPrima { get; set; }

    [Required]
    [StringLength(100)]
    public string Nombre { get; set; } = string.Empty;

    public string? Descripcion { get; set; }

    [Column(TypeName = "decimal(18,2)")]
    public decimal CostoUnitario { get; set; }

    public int Stock { get; set; }

    public int StockMinimo { get; set; }

    [Required]
    public int IdProveedor { get; set; }

    [ForeignKey(nameof(IdProveedor))]
    public Proveedor? Proveedor { get; set; }
   public ICollection<ProductoMateriaPrima> Productos { get; set; }
}
