using System.ComponentModel.DataAnnotations;

namespace CangureraInteligente.DTOs;

/// <summary>
/// Body del POST /api/recorridos/iniciar enviado por la app móvil.
/// </summary>
public record IniciarRecorridoRequest
{
	/// <summary>MAC del ESP32 que se presta. Ej: "24:0A:C4:8B:58:FC"</summary>
	[Required]
	[RegularExpression("^([0-9A-Fa-f]{2}:){5}[0-9A-Fa-f]{2}$", ErrorMessage = "Formato de MAC inválido. Esperado: XX:XX:XX:XX:XX:XX")]
	public string DispositivoMac { get; init; } = string.Empty;

	/// <summary>Edad del usuario (opcional).</summary>
	[Range(1, 120)]
	public int? UsuarioEdad { get; init; }

	/// <summary>ID de la discapacidad del catálogo (opcional).</summary>
	public int? DiscapacidadId { get; init; }
}
