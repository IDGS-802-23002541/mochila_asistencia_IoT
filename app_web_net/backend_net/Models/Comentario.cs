using System;
using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;

namespace CangureraInteligente.Models;

[Table("Comentarios", Schema = "Operativo")]
public class Comentario
{
    [Key]
    public int IdComentario { get; set; }

    [Required]
    [MaxLength(150)]
    public string NombreCliente { get; set; } = string.Empty;

    [Required]
    [MaxLength(150)]
    [EmailAddress]
    public string CorreoCliente { get; set; } = string.Empty;

    [Required]
    [MaxLength(1000)]
    public string Mensaje { get; set; } = string.Empty;

    public DateTime FechaCreacion { get; set; } = DateTime.UtcNow;

    [Required]
    [MaxLength(30)]
    public string Estado { get; set; } = "Pendiente";

    [MaxLength(1000)]
    public string? RespuestaAdministrador { get; set; }

    public DateTime? FechaRespuesta { get; set; }
}