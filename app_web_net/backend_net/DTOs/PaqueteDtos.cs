using System;
using System.Collections.Generic;
using System.ComponentModel.DataAnnotations;

namespace CangureraInteligente.DTOs
{
    public class ContenidoItemDto
    {
        [Required]
        public int IdItem { get; set; }

        [Range(1, int.MaxValue, ErrorMessage = "La cantidad debe ser mayor a 0.")]
        public int Cantidad { get; set; } = 1;
    }

    public class ContenidoDetalleDto
    {
        public int IdProductoContenido { get; set; }
        public int IdItem { get; set; }
        public string NombreItem { get; set; } = string.Empty;
        public int Cantidad { get; set; }
    }

    public class DocumentoDto
    {
        public int IdProductoDocumento { get; set; }
        public string NombreArchivo { get; set; } = string.Empty;
        public string TipoContenido { get; set; } = string.Empty;
        public string? Descripcion { get; set; }
        public DateTime FechaSubida { get; set; }
    }

    public class DocumentoCreateDto
    {
        [Required]
        [MaxLength(255)]
        public string NombreArchivo { get; set; } = string.Empty;

        [Required]
        [MaxLength(100)]
        public string TipoContenido { get; set; } = "application/octet-stream";

        [MaxLength(255)]
        public string? Descripcion { get; set; }

        [Required]
        public string ContenidoBase64 { get; set; } = string.Empty;
    }

    // Detalle visible para el cliente: SIN receta de materia prima,
    // sin margen de ganancia y sin stock.
    public class ProductoPublicoDto
    {
        public int IdProducto { get; set; }
        public string Nombre { get; set; } = string.Empty;
        public string? Descripcion { get; set; }
        public decimal Precio { get; set; }
        public string? FotoUrl { get; set; }
        public bool IncluyeMochila { get; set; }
        public List<ContenidoDetalleDto> Contenido { get; set; } = new();
        public List<DocumentoDto> Documentos { get; set; } = new();
    }
}