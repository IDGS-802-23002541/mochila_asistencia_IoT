using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;

namespace CangureraInteligente.Models;

[Table("DetalleVenta", Schema = "Operativo")]
public class DetalleVenta
{
    [Key]
    public int IdDetalleVenta { get; set; }

    public int IdVenta { get; set; }

    public int IdProducto { get; set; }

    public int Cantidad { get; set; }


    [Column(TypeName = "decimal(18,2)")]
    public decimal PrecioUnitario { get; set; }


    [ForeignKey(nameof(IdVenta))]
    public Venta? Venta { get; set; }


    [ForeignKey(nameof(IdProducto))]
    public Producto? Producto { get; set; }
}