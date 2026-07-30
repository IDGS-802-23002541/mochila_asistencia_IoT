using System.Linq;
using System.Threading;
using System.Threading.Tasks;
using CangureraInteligente.Data;
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

        return Ok(compras);
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


        return Ok(compra);
    }


    // POST: api/compras
    [HttpPost]
    public async Task<IActionResult> Create(
        [FromBody] Compra compra,
        CancellationToken ct)
    {
        if (!ModelState.IsValid)
        {
            return ValidationProblem(ModelState);
        }


        compra.IdCompra = 0;

        compra.FechaCompra = compra.FechaCompra == default
            ? DateTime.UtcNow
            : compra.FechaCompra;


        db.Compras.Add(compra);

        await db.SaveChangesAsync(ct);


        return CreatedAtAction(
            nameof(GetById),
            new
            {
                id = compra.IdCompra
            },
            compra);
    }


    // PUT: api/compras/{id}
    [HttpPut("{id:int}")]
    public async Task<IActionResult> Update(
        int id,
        [FromBody] Compra compra,
        CancellationToken ct)
    {
        if (id != compra.IdCompra &&
            compra.IdCompra != 0)
        {
            return BadRequest(new
            {
                error = "El id de la URL y el cuerpo no coinciden."
            });
        }


        var existente = await db.Compras
            .FirstOrDefaultAsync(
                c => c.IdCompra == id,
                ct);


        if (existente == null)
        {
            return NotFound(new
            {
                error = $"Compra {id} no encontrada."
            });
        }


        existente.IdProveedor = compra.IdProveedor;
        existente.FechaCompra = compra.FechaCompra;
        existente.Total = compra.Total;


        await db.SaveChangesAsync(ct);


        return Ok(existente);
    }


    // DELETE: api/compras/{id}
    [HttpDelete("{id:int}")]
    public async Task<IActionResult> Delete(
        int id,
        CancellationToken ct)
    {
        var compra = await db.Compras
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
}