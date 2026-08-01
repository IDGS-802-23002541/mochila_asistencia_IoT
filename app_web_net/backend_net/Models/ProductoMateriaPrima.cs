using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;

namespace CangureraInteligente.Models;

[Table("ProductoMateriaPrima", Schema = "Operativo")]
public class ProductoMateriaPrima
{
    public int IdProducto { get; set; }

    public int IdMateriaPrima { get; set; }

    [Column(TypeName = "decimal(18,2)")]
    public decimal Cantidad { get; set; }

    [ForeignKey(nameof(IdProducto))]
    public Producto? Producto { get; set; }

    [ForeignKey(nameof(IdMateriaPrima))]
    public MateriaPrima? MateriaPrima { get; set; }
}