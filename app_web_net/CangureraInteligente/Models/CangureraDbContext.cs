using CangureraInteligente.Models;
using Microsoft.EntityFrameworkCore;

namespace CangureraInteligente.Data;

public class CangureraDbContext(DbContextOptions<CangureraDbContext> options) : DbContext(options)
{
    public DbSet<Organizacion>       Organizaciones    { get; set; }
    public DbSet<Dispositivo>        Dispositivos      { get; set; }
    public DbSet<CatTipoEvento>      TiposEvento       { get; set; }
    public DbSet<CatTipoDiscapacidad> TiposDiscapacidad { get; set; }
    public DbSet<Recorrido>          Recorridos        { get; set; }
    public DbSet<EventoDetectado>    EventosDetectados { get; set; }
    public DbSet<ZonaCaliente>       ZonasCalientes    { get; set; }

    protected override void OnModelCreating(ModelBuilder mb)
    {
        mb.Entity<ZonaCaliente>()
            .Property(z => z.Latitud)
            .HasPrecision(9,6);

        mb.Entity<ZonaCaliente>()
            .Property(z => z.Longitud)
            .HasPrecision(9,6); 
        mb.Entity<EventoDetectado>()
            .Property(e =>e.DistanciaCm)
            .HasPrecision(7,2);
            
        // Índices únicos
        mb.Entity<Dispositivo>()
            .HasIndex(d => d.MacAddress)
            .IsUnique();

        mb.Entity<CatTipoEvento>()
            .HasIndex(t => t.NombreEvento)
            .IsUnique();

        mb.Entity<CatTipoDiscapacidad>()
            .HasIndex(d => d.Nombre)
            .IsUnique();

        // Columna MAC con collation case-insensitive en SQL Server
        mb.Entity<Dispositivo>()
            .Property(d => d.MacAddress)
            .UseCollation("SQL_Latin1_General_CP1_CI_AS");

        // Ruta_Coordenadas: EF no valida el JSON, solo lo persiste como string
        mb.Entity<Recorrido>()
            .Property(r => r.Ruta_Coordenadas)
            .HasColumnType("varchar(max)");
    }
}