using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;

namespace CangureraInteligente.Models;

[Table("ProductoContenido", Schema = "Operativo")]
public class ProductoContenido
{
    [Key]
    public int IdProductoContenido { get; set; }

    public int IdProducto { get; set; }

    public int IdItem { get; set; }

    public int Cantidad { get; set; } = 1;

    [ForeignKey(nameof(IdProducto))]
    public Producto? Producto { get; set; }

    [ForeignKey(nameof(IdItem))]
    public Producto? Item { get; set; }
}