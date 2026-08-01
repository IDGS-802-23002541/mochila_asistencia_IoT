using CangureraInteligente.Models;
using Microsoft.EntityFrameworkCore;

namespace CangureraInteligente.Data;

public class CangureraDbContext : DbContext
{
	public DbSet<Organizacion> Organizaciones { get; set; }

	public DbSet<Usuario> Usuarios { get; set; }

	public DbSet<Dispositivo> Dispositivos { get; set; }

	public DbSet<CatTipoEvento> TiposEvento { get; set; }

	public DbSet<Recorrido> Recorridos { get; set; }

	public DbSet<RecorridoCoordenada> RecorridoCoordenadas { get; set; }

	public DbSet<EventoDetectado> EventosDetectados { get; set; }

	// --- Nuevo: módulo de compras/ventas/inventario ---
    public DbSet<Compra> Compras { get; set; }
    public DbSet<DetalleCompra> DetallesCompra { get; set; }
    public DbSet<Venta> Ventas { get; set; }
    public DbSet<DetalleVenta> DetallesVenta { get; set; }
    public DbSet<Producto> Productos { get; set; }
    public DbSet<MateriaPrima> MateriasPrimas { get; set; }
    public DbSet<Proveedor> Proveedores { get; set; }
    public DbSet<ProductoMateriaPrima> ProductoMateriaPrima { get; set; }

	public CangureraDbContext(DbContextOptions<CangureraDbContext> options)
		: base(options)
	{
	}

	protected override void OnModelCreating(ModelBuilder mb)
	{
		mb.Entity<RecorridoCoordenada>().Property((RecorridoCoordenada c) => c.Latitud).HasPrecision(9, 6);
		mb.Entity<RecorridoCoordenada>().Property((RecorridoCoordenada c) => c.Longitud).HasPrecision(9, 6);
		mb.Entity<EventoDetectado>().Property((EventoDetectado e) => e.DistanciaCm).HasPrecision(7, 2);
		mb.Entity<Dispositivo>().HasIndex((Dispositivo d) => d.MacAddress).IsUnique();
		mb.Entity<CatTipoEvento>().HasIndex((CatTipoEvento t) => t.NombreEvento).IsUnique();
		mb.Entity<Dispositivo>().Property((Dispositivo d) => d.MacAddress).UseCollation("SQL_Latin1_General_CP1_CI_AS");

		// Nuevo: llave compuesta para tabla intermedia
        mb.Entity<ProductoMateriaPrima>().HasKey(pm => new { pm.IdProducto, pm.IdMateriaPrima });
	}
}
