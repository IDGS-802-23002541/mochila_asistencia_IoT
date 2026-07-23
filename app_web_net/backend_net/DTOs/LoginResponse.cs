namespace CangureraInteligente.DTOs;

public record LoginResponse
{
	public int Id { get; init; }

	public string Nombre { get; init; } = string.Empty;

	public string Correo { get; init; } = string.Empty;

	public string Rol { get; init; } = string.Empty;

	public int OrganizacionId { get; init; }

	public bool Estado_Activo { get; init; }

	public string Mensaje { get; init; } = "Login exitoso";
}
