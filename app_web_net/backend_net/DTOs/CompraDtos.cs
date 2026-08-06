using System;
using System.Collections.Generic;
using System.ComponentModel.DataAnnotations;

namespace CangureraInteligente.DTOs
{
    public class DetalleCompraCreateDto
    {
        [Required]
        public int IdMateriaPrima { get; set; }

        [Range(1, int.MaxValue, ErrorMessage = "La cantidad debe ser mayor a 0.")]
        public int Cantidad { get; set; }

        [Range(0, double.MaxValue)]
        public decimal PrecioUnitario { get; set; }
    }

    public class CompraCreateDto
    {
        [Required]
        public int IdProveedor { get; set; }

        public DateTime? FechaCompra { get; set; }

        [MinLength(1, ErrorMessage = "La compra debe tener al menos un detalle.")]
        public List<DetalleCompraCreateDto> Detalles { get; set; } = new();
    }

    public class DetalleCompraResponseDto
    {
        public int IdDetalleCompra { get; set; }
        public int IdMateriaPrima { get; set; }
        public string NombreMateriaPrima { get; set; } = string.Empty;
        public int Cantidad { get; set; }
        public decimal PrecioUnitario { get; set; }
        public decimal Subtotal { get; set; }
    }

    public class CompraResponseDto
    {
        public int IdCompra { get; set; }
        public DateTime FechaCompra { get; set; }
        public int IdProveedor { get; set; }
        public string NombreProveedor { get; set; } = string.Empty;
        public decimal Total { get; set; }
        public List<DetalleCompraResponseDto> Detalles { get; set; } = new();
    }
}
