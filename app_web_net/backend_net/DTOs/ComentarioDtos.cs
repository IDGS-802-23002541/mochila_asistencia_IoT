using System;

namespace CangureraInteligente.DTOs;

public class CrearComentarioDto
{
    public string NombreCliente { get; set; } = string.Empty;
    public string CorreoCliente { get; set; } = string.Empty;
    public string Mensaje { get; set; } = string.Empty;
}

public class ActualizarComentarioDto
{
    public string Estado { get; set; } = string.Empty;
    public string? RespuestaAdministrador { get; set; }
}

public class ComentarioResponseDto
{
    public int IdComentario { get; set; }
    public string NombreCliente { get; set; } = string.Empty;
    public string CorreoCliente { get; set; } = string.Empty;
    public string Mensaje { get; set; } = string.Empty;
    public string Estado { get; set; } = string.Empty;
    public string? RespuestaAdministrador { get; set; }
    public DateTime FechaCreacion { get; set; }
    public DateTime? FechaRespuesta { get; set; }
}