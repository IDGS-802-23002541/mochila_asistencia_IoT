using System.Linq;
using System.Threading;
using System.Threading.Tasks;
using CangureraInteligente.Data;
using CangureraInteligente.Models;
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;

namespace CangureraInteligente.Controllers;

[ApiController]
[Route("api/detalles-compra")]
[Produces("application/json")]
public class DetallesCompraController(CangureraDbContext db) : ControllerBase
{
    // GET: api/detalles-compra
    [HttpGet]
    public async Task<IActionResult> GetAll(CancellationToken ct)
    {
        var detalles = await db.DetallesCompra
            .Include(d => d.Compra)
            .Include(d => d.MateriaPrima)
            .AsNoTracking()
            .OrderBy(d => d.IdDetalleCompra)
            .ToListAsync(ct);

        return Ok(detalles);
    }


    // GET: api/detalles-compra/{id}
    [HttpGet("{id:int}")]
    public async Task<IActionResult> GetById(
        int id,
        CancellationToken ct)
    {
        var detalle = await db.DetallesCompra
            .Include(d => d.Compra)
            .Include(d => d.MateriaPrima)
            .AsNoTracking()
            .FirstOrDefaultAsync(
                d => d.IdDetalleCompra == id,
                ct);


        if (detalle == null)
        {
            return NotFound(new
            {
                error = $"Detalle de compra {id} no encontrado."
            });
        }


        return Ok(detalle);
    }


    // POST: api/detalles-compra
    [HttpPost]
    public async Task<IActionResult> Create(
        [FromBody] DetalleCompra detalle,
        CancellationToken ct)
    {
        if (!ModelState.IsValid)
        {
            return ValidationProblem(ModelState);
        }


        detalle.IdDetalleCompra = 0;


        var materiaPrima = await db.MateriasPrimas
            .FirstOrDefaultAsync(
                m => m.IdMateriaPrima == detalle.IdMateriaPrima,
                ct);


        if (materiaPrima == null)
        {
            return NotFound(new
            {
                error = "La materia prima no existe."
            });
        }


        // Actualiza inventario
        materiaPrima.Stock += (int)detalle.Cantidad;


        db.DetallesCompra.Add(detalle);

        await db.SaveChangesAsync(ct);


        return CreatedAtAction(
            nameof(GetById),
            new
            {
                id = detalle.IdDetalleCompra
            },
            detalle);
    }


    // PUT: api/detalles-compra/{id}
    [HttpPut("{id:int}")]
    public async Task<IActionResult> Update(
        int id,
        [FromBody] DetalleCompra detalle,
        CancellationToken ct)
    {
        if (id != detalle.IdDetalleCompra &&
            detalle.IdDetalleCompra != 0)
        {
            return BadRequest(new
            {
                error = "El id de la URL y el cuerpo no coinciden."
            });
        }


        var existente = await db.DetallesCompra
            .FirstOrDefaultAsync(
                d => d.IdDetalleCompra == id,
                ct);


        if (existente == null)
        {
            return NotFound(new
            {
                error = $"Detalle de compra {id} no encontrado."
            });
        }


        existente.IdCompra = detalle.IdCompra;
        existente.IdMateriaPrima = detalle.IdMateriaPrima;
        existente.Cantidad = detalle.Cantidad;
        existente.PrecioUnitario = detalle.PrecioUnitario;


        await db.SaveChangesAsync(ct);


        return Ok(existente);
    }


    // DELETE: api/detalles-compra/{id}
    [HttpDelete("{id:int}")]
    public async Task<IActionResult> Delete(
        int id,
        CancellationToken ct)
    {
        var detalle = await db.DetallesCompra
            .FirstOrDefaultAsync(
                d => d.IdDetalleCompra == id,
                ct);


        if (detalle == null)
        {
            return NotFound(new
            {
                error = $"Detalle de compra {id} no encontrado."
            });
        }


        db.DetallesCompra.Remove(detalle);


        try
        {
            await db.SaveChangesAsync(ct);
        }
        catch (DbUpdateException)
        {
            return Conflict(new
            {
                error = "No se puede eliminar el detalle de compra."
            });
        }


        return NoContent();
    }
}