using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;

namespace CangureraInteligente.Models;

// ── Operativo.Organizaciones ──────────────────────────────────────────────
[Table("Organizaciones", Schema = "Operativo")]
public class Organizacion
{
    [Key]
    public int Id { get; set; }

    [Required, MaxLength(150)]
    public string Nombre { get; set; } = string.Empty;

    [Required, MaxLength(50)]
    public string Sector { get; set; } = string.Empty;

    [MaxLength(100)]
    public string? Contacto_Principal { get; set; }

    [MaxLength(100)]
    public string? Email_Contacto { get; set; }

    public DateTime FechaCreacion { get; set; } = DateTime.UtcNow;
    public bool Estado_Activo { get; set; } = true;

    // Nav
    public ICollection<Dispositivo> Dispositivos { get; set; } = [];
}

// ── Operativo.Dispositivos ────────────────────────────────────────────────
[Table("Dispositivos", Schema = "Operativo")]
public class Dispositivo
{
    [Key]
    public int Id { get; set; }

    public int OrganizacionId { get; set; }

    [Required, MaxLength(17)]
    public string MacAddress { get; set; } = string.Empty;

    public DateTime FechaRegistro { get; set; } = DateTime.UtcNow;
    public DateTime? UltimaConexion { get; set; }

    [MaxLength(20)]
    public string Estado { get; set; } = "Activo";

    // Nav
    [ForeignKey(nameof(OrganizacionId))]
    public Organizacion Organizacion { get; set; } = null!;

    public ICollection<Recorrido> Recorridos { get; set; } = [];
}

// ── Operativo.Cat_TiposEvento ─────────────────────────────────────────────
[Table("Cat_TiposEvento", Schema = "Operativo")]
public class CatTipoEvento
{
    [Key]
    public int Id { get; set; }

    [Required, MaxLength(50)]
    public string NombreEvento { get; set; } = string.Empty;

    [Required, MaxLength(20)]
    public string Severidad { get; set; } = string.Empty;
}

// ── Operativo.Cat_TiposDiscapacidad ──────────────────────────────────────
[Table("Cat_TiposDiscapacidad", Schema = "Operativo")]
public class CatTipoDiscapacidad
{
    [Key]
    public int Id { get; set; }

    [Required, MaxLength(50)]
    public string Nombre { get; set; } = string.Empty;
}

// ── Operativo.Recorridos ──────────────────────────────────────────────────
[Table("Recorridos", Schema = "Operativo")]
public class Recorrido
{
    [Key]
    public int Id { get; set; }

    public int DispositivoId { get; set; }

    public DateTime FechaInicio { get; set; } = DateTime.UtcNow;
    public DateTime? FechaFin { get; set; }

    public int? Usuario_Edad { get; set; }
    public int? DiscapacidadId { get; set; }

    // JSON almacenado como string (validado con CHECK ISJSON en SQL)
    public string? Ruta_Coordenadas { get; set; }

    // Nav
    [ForeignKey(nameof(DispositivoId))]
    public Dispositivo Dispositivo { get; set; } = null!;

    [ForeignKey(nameof(DiscapacidadId))]
    public CatTipoDiscapacidad? Discapacidad { get; set; }

    public ICollection<EventoDetectado> Eventos { get; set; } = [];
}

// ── Operativo.Eventos_Detectados ──────────────────────────────────────────
[Table("Eventos_Detectados", Schema = "Operativo")]
public class EventoDetectado
{
    [Key]
    public long Id { get; set; }

    public int RecorridoId { get; set; }
    public int TipoEventoId { get; set; }

    public DateTime TimestampEvento { get; set; } = DateTime.UtcNow;

    [Column(TypeName = "decimal(10,8)")]
    public decimal? Latitud { get; set; }

    [Column(TypeName = "decimal(10,8)")]
    public decimal? Longitud { get; set; }

    public bool Geo_Es_Estimado { get; set; } = false;

    [Column(TypeName = "decimal(5,2)")]
    public decimal? FuerzaImpactoG { get; set; }

    // Nav
    [ForeignKey(nameof(RecorridoId))]
    public Recorrido Recorrido { get; set; } = null!;

    [ForeignKey(nameof(TipoEventoId))]
    public CatTipoEvento TipoEvento { get; set; } = null!;
}