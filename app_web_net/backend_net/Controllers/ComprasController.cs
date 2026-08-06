using System.Linq;
using System.Threading;
using System.Threading.Tasks;
using CangureraInteligente.Data;
using CangureraInteligente.DTOs;
using CangureraInteligente.Models;
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using System;

namespace CangureraInteligente.Controllers;

[ApiController]
[Route("api/compras")]
[Produces("application/json")]
public class ComprasController(CangureraDbContext db) : ControllerBase
{
    // GET: api/compras
    [HttpGet]
    public async Task<IActionResult> GetAll(CancellationToken ct)
    {
        var compras = await db.Compras
            .Include(c => c.Proveedor)
            .Include(c => c.Detalles)
                .ThenInclude(d => d.MateriaPrima)
            .AsNoTracking()
            .OrderBy(c => c.IdCompra)
            .ToListAsync(ct);

        return Ok(compras.Select(ToResponse));
    }

    // GET: api/compras/{id}
    [HttpGet("{id:int}")]
    public async Task<IActionResult> GetById(int id, CancellationToken ct)
    {
        var compra = await db.Compras
            .Include(c => c.Proveedor)
            .Include(c => c.Detalles)
                .ThenInclude(d => d.MateriaPrima)
            .AsNoTracking()
            .FirstOrDefaultAsync(
                c => c.IdCompra == id,
                ct);

        if (compra == null)
        {
            return NotFound(new
            {
                error = $"Compra {id} no encontrada."
            });
        }

        return Ok(ToResponse(compra));
    }

    // POST: api/compras
    // Crea la compra junto con sus detalles y actualiza el stock
    // de las materias primas en una sola transacción.
    [HttpPost]
    public async Task<IActionResult> Create(
        [FromBody] CompraCreateDto dto,
        CancellationToken ct)
    {
        if (!ModelState.IsValid)
        {
            return ValidationProblem(ModelState);
        }

        // Validar que el proveedor exista.
        var proveedor = await db.Proveedores
            .AsNoTracking()
            .FirstOrDefaultAsync(p => p.IdProveedor == dto.IdProveedor, ct);

        if (proveedor == null)
        {
            return NotFound(new
            {
                error = $"Proveedor {dto.IdProveedor} no encontrado."
            });
        }

        // Validar que no haya materias primas repetidas en la misma compra.
        var idsRepetidos = dto.Detalles
            .GroupBy(d => d.IdMateriaPrima)
            .Where(g => g.Count() > 1)
            .Select(g => g.Key)
            .ToList();

        if (idsRepetidos.Count > 0)
        {
            return BadRequest(new
            {
                error = "La compra tiene materias primas repetidas.",
                idsMateriaPrima = idsRepetidos
            });
        }

        // Validar que todas las materias primas existan.
        var idsRecibidos = dto.Detalles.Select(d => d.IdMateriaPrima).ToList();

        var materias = await db.MateriasPrimas
            .Where(m => idsRecibidos.Contains(m.IdMateriaPrima))
            .ToListAsync(ct);

        var idsExistentes = materias.Select(m => m.IdMateriaPrima).ToList();
        var idsInexistentes = idsRecibidos.Except(idsExistentes).ToList();

        if (idsInexistentes.Count > 0)
        {
            return BadRequest(new
            {
                error = "Alguna(s) materia(s) prima no existe(n).",
                idsMateriaPrima = idsInexistentes
            });
        }

        var total = dto.Detalles.Sum(d => d.Cantidad * d.PrecioUnitario);

        var compra = new Compra
        {
            IdProveedor = dto.IdProveedor,
            FechaCompra = dto.FechaCompra ?? DateTime.UtcNow,
            Total = total
        };

        db.Compras.Add(compra);
        await db.SaveChangesAsync(ct);

        // Insertar detalles y sumar stock de cada materia prima.
        foreach (var d in dto.Detalles)
        {
            db.DetallesCompra.Add(new DetalleCompra
            {
                IdCompra = compra.IdCompra,
                IdMateriaPrima = d.IdMateriaPrima,
                Cantidad = d.Cantidad,
                PrecioUnitario = d.PrecioUnitario
            });

            var materia = materias.First(m => m.IdMateriaPrima == d.IdMateriaPrima);
            materia.Stock += d.Cantidad;
        }

        await db.SaveChangesAsync(ct);

        return CreatedAtAction(
            nameof(GetById),
            new { id = compra.IdCompra },
            new { compra.IdCompra });
    }

    // PUT: api/compras/{id}
    // Solo actualiza datos de cabecera; los detalles se manejan por separado.
    [HttpPut("{id:int}")]
    public async Task<IActionResult> Update(
        int id,
        [FromBody] CompraCreateDto dto,
        CancellationToken ct)
    {
        if (!ModelState.IsValid)
        {
            return ValidationProblem(ModelState);
        }

        var existente = await db.Compras
            .Include(c => c.Detalles)
            .FirstOrDefaultAsync(c => c.IdCompra == id, ct);

        if (existente == null)
        {
            return NotFound(new
            {
                error = $"Compra {id} no encontrada."
            });
        }

        var proveedor = await db.Proveedores
            .AsNoTracking()
            .FirstOrDefaultAsync(p => p.IdProveedor == dto.IdProveedor, ct);

        if (proveedor == null)
        {
            return NotFound(new
            {
                error = $"Proveedor {dto.IdProveedor} no encontrado."
            });
        }

        var idsRecibidos = dto.Detalles.Select(d => d.IdMateriaPrima).ToList();

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

        // Revertir el stock de los detalles anteriores antes de aplicar los nuevos.
        foreach (var detalle in existente.Detalles)
        {
            var materia = await db.MateriasPrimas
                .FirstOrDefaultAsync(m => m.IdMateriaPrima == detalle.IdMateriaPrima, ct);

            if (materia != null)
            {
                materia.Stock -= detalle.Cantidad;
            }
        }

        existente.IdProveedor = dto.IdProveedor;
        existente.FechaCompra = dto.FechaCompra ?? existente.FechaCompra;
        existente.Total = dto.Detalles.Sum(d => d.Cantidad * d.PrecioUnitario);

        db.DetallesCompra.RemoveRange(existente.Detalles);

        foreach (var d in dto.Detalles)
        {
            db.DetallesCompra.Add(new DetalleCompra
            {
                IdCompra = existente.IdCompra,
                IdMateriaPrima = d.IdMateriaPrima,
                Cantidad = d.Cantidad,
                PrecioUnitario = d.PrecioUnitario
            });

            var materia = await db.MateriasPrimas
                .FirstOrDefaultAsync(m => m.IdMateriaPrima == d.IdMateriaPrima, ct);

            if (materia != null)
            {
                materia.Stock += d.Cantidad;
            }
        }

        await db.SaveChangesAsync(ct);

        return Ok(new { existente.IdCompra });
    }

    // DELETE: api/compras/{id}
    [HttpDelete("{id:int}")]
    public async Task<IActionResult> Delete(int id, CancellationToken ct)
    {
        var compra = await db.Compras
            .Include(c => c.Detalles)
            .FirstOrDefaultAsync(c => c.IdCompra == id, ct);

        if (compra == null)
        {
            return NotFound(new
            {
                error = $"Compra {id} no encontrada."
            });
        }

        // Revertir el stock antes de eliminar.
        foreach (var d in compra.Detalles)
        {
            var materia = await db.MateriasPrimas
                .FirstOrDefaultAsync(m => m.IdMateriaPrima == d.IdMateriaPrima, ct);

            if (materia != null)
            {
                materia.Stock -= d.Cantidad;
            }
        }

        db.Compras.Remove(compra);

        try
        {
            await db.SaveChangesAsync(ct);
        }
        catch (DbUpdateException)
        {
            return Conflict(new
            {
                error = "No se puede eliminar la compra porque tiene detalles asociados."
            });
        }

        return NoContent();
    }

    private static object ToResponse(Compra compra)
    {
        return new CompraResponseDto
        {
            IdCompra = compra.IdCompra,
            FechaCompra = compra.FechaCompra,
            IdProveedor = compra.IdProveedor,
            NombreProveedor = compra.Proveedor?.Nombre ?? string.Empty,
            Total = compra.Total,
            Detalles = compra.Detalles
                .Select(d => new DetalleCompraResponseDto
                {
                    IdDetalleCompra = d.IdDetalleCompra,
                    IdMateriaPrima = d.IdMateriaPrima,
                    NombreMateriaPrima = d.MateriaPrima?.Nombre ?? string.Empty,
                    Cantidad = d.Cantidad,
                    PrecioUnitario = d.PrecioUnitario,
                    Subtotal = d.Cantidad * d.PrecioUnitario
                })
                .ToList()
        };
    }
}