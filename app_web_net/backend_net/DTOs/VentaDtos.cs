using System;
using System.Collections.Generic;

namespace CangureraInteligente.DTOs
{
    // Información de producto visible para el cliente: sin receta,
    // sin margen de ganancia y sin stock.
    public class ProductoVentaDto
    {
        public int IdProducto { get; set; }
        public string Nombre { get; set; } = string.Empty;
        public string? FotoUrl { get; set; }
    }

    public class VentaItemDto
    {
        public int IdDetalleVenta { get; set; }
        public int IdVenta { get; set; }
        public int IdProducto { get; set; }
        public int Cantidad { get; set; }
        public decimal PrecioUnitario { get; set; }
        public ProductoVentaDto? Producto { get; set; }
    }

    public class VentaResponseDto
    {
        public int IdVenta { get; set; }
        public DateTime FechaVenta { get; set; }
        public decimal Total { get; set; }
        public int IdOrganizacion { get; set; }
        public List<VentaItemDto> Detalles { get; set; } = new();
    }
}