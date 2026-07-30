using System;
using System.Collections.Generic;
using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;

namespace CangureraInteligente.Models;

[Table("Productos", Schema = "Operativo")]
public class Producto
{
    [Key]
    public int IdProducto { get; set; }

    [Required]
    [StringLength(100)]
    public string Nombre { get; set; } = string.Empty;

    public string? Descripcion { get; set; }

    [Column(TypeName = "decimal(18,2)")]
    public decimal Precio { get; set; }

    public int Stock { get; set; }

    [Column(TypeName = "decimal(5,2)")]
    public decimal MargenGanancia { get; set; } = 20;

    public bool Activo { get; set; } = true;

    public ICollection<ProductoMateriaPrima> MateriasPrimas { get; set; }
}