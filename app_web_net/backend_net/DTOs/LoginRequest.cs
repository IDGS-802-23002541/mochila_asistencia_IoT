using System.ComponentModel.DataAnnotations;

namespace CangureraInteligente.DTOs;

public record LoginRequest
{
	[Required]
	[EmailAddress]
	public string Correo { get; init; } = string.Empty;

	[Required]
	public string Contrasena { get; init; } = string.Empty;
}
