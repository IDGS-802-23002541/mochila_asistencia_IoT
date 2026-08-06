using CangureraInteligente.Models;

namespace CangureraInteligente.DTOs
{
    public class MateriaPrimaResponseDto
    {
        public int IdMateriaPrima { get; set; }
        public string Nombre { get; set; } = string.Empty;
        public string? Descripcion { get; set; }
        public decimal CostoUnitario { get; set; }
        public decimal? PrecioPromedio { get; set; }
        public int Stock { get; set; }
        public int StockMinimo { get; set; }
        public int IdProveedor { get; set; }
        public ProveedorResumenDto? Proveedor { get; set; }
    }

    public class ProveedorResumenDto
    {
        public int IdProveedor { get; set; }
        public string Nombre { get; set; } = string.Empty;
    }
}