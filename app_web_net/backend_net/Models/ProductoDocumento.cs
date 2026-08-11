using System;
using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;

namespace CangureraInteligente.Models;

[Table("ProductoDocumento", Schema = "Operativo")]
public class ProductoDocumento
{
    [Key]
    public int IdProductoDocumento { get; set; }

    public int IdProducto { get; set; }

    [Required]
    [MaxLength(255)]
    public string NombreArchivo { get; set; } = string.Empty;

    [Required]
    [MaxLength(100)]
    public string TipoContenido { get; set; } = "application/octet-stream";

    [MaxLength(255)]
    public string? Descripcion { get; set; }

    public string ContenidoBase64 { get; set; } = string.Empty;

    public DateTime FechaSubida { get; set; } = DateTime.UtcNow;

    [ForeignKey(nameof(IdProducto))]
    public Producto? Producto { get; set; }
}