using System.Collections.Generic;
using System.ComponentModel.DataAnnotations;

namespace CangureraInteligente.DTOs
{
    public class RecetaItemDto
    {
        [Required]
        public int IdMateriaPrima { get; set; }

        [Range(0.01, double.MaxValue, ErrorMessage = "La cantidad debe ser mayor a 0.")]
        public decimal Cantidad { get; set; }
    }
    public class ProductoCreateDto
    {
        [Required]
        [StringLength(100)]
        public string Nombre { get; set; } = string.Empty;

        public string? Descripcion { get; set; }

        [Range(0, double.MaxValue)]
        public decimal Precio { get; set; }

        [Range(0, int.MaxValue)]
        public int Stock { get; set; }

        [Range(0, 100)]
        public decimal MargenGanancia { get; set; } = 20;

        public bool Activo { get; set; } = true;

        public string? FotoUrl { get; set; }

        [Required]
        [MinLength(1, ErrorMessage = "El producto debe tener al menos una materia prima en su receta.")]
        public List<RecetaItemDto> Receta { get; set; } = new();
    }
    public class RecetaDetalleItemDto
    {
        public int IdMateriaPrima { get; set; }
        public string NombreMateriaPrima { get; set; } = string.Empty;
        public decimal Cantidad { get; set; }
        public decimal CostoUnitario { get; set; }
    }

    public class ProductoDetalleDto
    {
        public int IdProducto { get; set; }
        public string Nombre { get; set; } = string.Empty;
        public string? Descripcion { get; set; }
        public decimal Precio { get; set; }
        public int Stock { get; set; }
        public decimal MargenGanancia { get; set; }
        public bool Activo { get; set; }
        public string? FotoUrl { get; set; }
        public List<RecetaDetalleItemDto> Receta { get; set; } = new();
    }


}
