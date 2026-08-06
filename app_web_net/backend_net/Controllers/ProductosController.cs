using CangureraInteligente.Data;
using CangureraInteligente.DTOs;
using CangureraInteligente.Models;
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using System.Linq;
using System.Threading;
using System.Threading.Tasks;

namespace CangureraInteligente.Controllers;

[ApiController]
[Route("api/productos")]
[Produces("application/json")]
public class ProductosController(CangureraDbContext db) : ControllerBase
{
    // GET: api/productos
    [HttpGet]
    public async Task<IActionResult> GetAll(CancellationToken ct)
    {
        var productos = await db.Productos
            .AsNoTracking()
            .OrderBy(p => p.IdProducto)
            .ToListAsync(ct);

        return Ok(productos);
    }

    // GET: api/productos/{id}
    [HttpGet("{id:int}")]
    public async Task<IActionResult> GetById(
        int id,
        CancellationToken ct)
    {
        var producto = await db.Productos
            .AsNoTracking()
            .FirstOrDefaultAsync(
                p => p.IdProducto == id,
                ct);


        if (producto == null)
        {
            return NotFound(new
            {
                error = $"Producto {id} no encontrado."
            });
        }


        return Ok(producto);
    }

    // GET: api/productos/{id}/detalle
    [HttpGet("{id:int}/detalle")]
    public async Task<IActionResult> GetDetalle(
        int id,
        CancellationToken ct)
    {
        var producto = await db.Productos
            .AsNoTracking()
            .Where(p => p.IdProducto == id)
            .Select(p => new ProductoDetalleDto
            {
                IdProducto = p.IdProducto,
                Nombre = p.Nombre,
                Descripcion = p.Descripcion,
                Precio = p.Precio,
                Stock = p.Stock,
                MargenGanancia = p.MargenGanancia,
                Activo = p.Activo,
                FotoUrl = p.FotoUrl,
                Receta = p.MateriasPrimas
                    .Select(mp => new RecetaDetalleItemDto
                    {
                        IdMateriaPrima = mp.IdMateriaPrima,
                        NombreMateriaPrima = mp.MateriaPrima!.Nombre,
                        Cantidad = mp.Cantidad,
                        CostoUnitario = mp.MateriaPrima!.CostoUnitario
                    })
                    .OrderBy(r => r.NombreMateriaPrima)
                    .ToList()
            })
            .FirstOrDefaultAsync(ct);

        if (producto == null)
        {
            return NotFound(new
            {
                error = $"Producto {id} no encontrado."
            });
        }

        return Ok(producto);
    }

    // POST: api/productos
    [HttpPost]
    public async Task<IActionResult> Create(
        [FromBody] ProductoCreateDto dto,
        CancellationToken ct)
    {
        if (!ModelState.IsValid)
        {
            return ValidationProblem(ModelState);
        }

        // No permitir materias primas repetidas dentro de la misma receta.
        var idsRepetidos = dto.Receta
            .GroupBy(r => r.IdMateriaPrima)
            .Where(g => g.Count() > 1)
            .Select(g => g.Key)
            .ToList();

        if (idsRepetidos.Count > 0)
        {
            return BadRequest(new
            {
                error = "La receta tiene materias primas repetidas.",
                idsMateriaPrima = idsRepetidos
            });
        }

        // Validar que todas las materias primas de la receta existan.
        var idsRecibidos = dto.Receta.Select(r => r.IdMateriaPrima).ToList();

        var idsExistentes = await db.MateriasPrimas
            .Where(m => idsRecibidos.Contains(m.IdMateriaPrima))
            .Select(m => m.IdMateriaPrima)
            .ToListAsync(ct);

        var idsInexistentes = idsRecibidos.Except(idsExistentes).ToList();

        if (idsInexistentes.Count > 0)
        {
            return BadRequest(new
            {
                error = "Alguna(s) materia(s) prima no existe(n).",
                idsMateriaPrima = idsInexistentes
            });
        }

        var producto = new Producto
        {
            Nombre = dto.Nombre,
            Descripcion = dto.Descripcion,
            Precio = dto.Precio,
            Stock = dto.Stock,
            MargenGanancia = dto.MargenGanancia,
            Activo = dto.Activo,
            FotoUrl = dto.FotoUrl,
            MateriasPrimas = dto.Receta
                .Select(r => new ProductoMateriaPrima
                {
                    IdMateriaPrima = r.IdMateriaPrima,
                    Cantidad = r.Cantidad
                })
                .ToList()
        };

        db.Productos.Add(producto);
        await db.SaveChangesAsync(ct);

        return CreatedAtAction(
            nameof(GetDetalle),
            new
            {
                id = producto.IdProducto
            },
            new
            {
                producto.IdProducto
            });
    }

    // PUT: api/productos/{id}
    [HttpPut("{id:int}")]
    public async Task<IActionResult> Update(
        int id,
        [FromBody] ProductoCreateDto dto,
        CancellationToken ct)
    {
        if (!ModelState.IsValid)
        {
            return ValidationProblem(ModelState);
        }

        var existente = await db.Productos
            .Include(p => p.MateriasPrimas)
            .FirstOrDefaultAsync(
                p => p.IdProducto == id,
                ct);

        if (existente == null)
        {
            return NotFound(new
            {
                error = $"Producto {id} no encontrado."
            });
        }

        var idsRepetidos = dto.Receta
            .GroupBy(r => r.IdMateriaPrima)
            .Where(g => g.Count() > 1)
            .Select(g => g.Key)
            .ToList();

        if (idsRepetidos.Count > 0)
        {
            return BadRequest(new
            {
                error = "La receta tiene materias primas repetidas.",
                idsMateriaPrima = idsRepetidos
            });
        }

        var idsRecibidos = dto.Receta.Select(r => r.IdMateriaPrima).ToList();

        var idsExistentes = await db.MateriasPrimas
            .Where(m => idsRecibidos.Contains(m.IdMateriaPrima))
            .Select(m => m.IdMateriaPrima)
            .ToListAsync(ct);

        var idsInexistentes = idsRecibidos.Except(idsExistentes).ToList();

        if (idsInexistentes.Count > 0)
        {
            return BadRequest(new
            {
                error = "Alguna(s) materia(s) prima no existe(n).",
                idsMateriaPrima = idsInexistentes
            });
        }

        existente.Nombre = dto.Nombre;
        existente.Descripcion = dto.Descripcion;
        existente.Precio = dto.Precio;
        existente.Stock = dto.Stock;
        existente.MargenGanancia = dto.MargenGanancia;
        existente.Activo = dto.Activo;
        existente.FotoUrl = dto.FotoUrl;

        db.ProductoMateriaPrima.RemoveRange(existente.MateriasPrimas);
        existente.MateriasPrimas = dto.Receta
            .Select(r => new ProductoMateriaPrima
            {
                IdProducto = id,
                IdMateriaPrima = r.IdMateriaPrima,
                Cantidad = r.Cantidad
            })
            .ToList();

        await db.SaveChangesAsync(ct);

        return Ok(new
        {
            existente.IdProducto
        });
    }


    // DELETE: api/productos/{id}
    [HttpDelete("{id:int}")]
    public async Task<IActionResult> Delete(
        int id,
        CancellationToken ct)
    {
        var producto = await db.Productos
            .FirstOrDefaultAsync(
                p => p.IdProducto == id,
                ct);


        if (producto == null)
        {
            return NotFound(new
            {
                error = $"Producto {id} no encontrado."
            });
        }


        db.Productos.Remove(producto);


        try
        {
            await db.SaveChangesAsync(ct);
        }
        catch (DbUpdateException)
        {
            return Conflict(new
            {
                error = "No se puede eliminar el producto porque tiene materiales asociados."
            });
        }


        return NoContent();
    }

}