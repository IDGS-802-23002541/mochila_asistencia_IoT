using System.Linq;
using System.Threading;
using System.Threading.Tasks;
using CangureraInteligente.Data;
using CangureraInteligente.Models;
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;

namespace CangureraInteligente.Controllers;

[ApiController]
[Route("api/producto-materia-prima")]
[Produces("application/json")]
public class ProductoMateriaPrimaController(CangureraDbContext db) : ControllerBase
{
    // GET: api/producto-materia-prima
    [HttpGet]
    public async Task<IActionResult> GetAll(CancellationToken ct)
    {
        var datos = await db.ProductoMateriaPrima
            .Include(pm => pm.Producto)
            .Include(pm => pm.MateriaPrima)
            .AsNoTracking()
            .ToListAsync(ct);

        return Ok(datos);
    }


    // GET: api/producto-materia-prima/producto/1
    [HttpGet("producto/{id:int}")]
    public async Task<IActionResult> GetByProducto(
        int id,
        CancellationToken ct)
    {
        var datos = await db.ProductoMateriaPrima
            .Include(pm => pm.MateriaPrima)
            .Where(pm => pm.IdProducto == id)
            .AsNoTracking()
            .ToListAsync(ct);

        return Ok(datos);
    }


    // POST: api/producto-materia-prima
    [HttpPost]
    public async Task<IActionResult> Create(
        [FromBody] ProductoMateriaPrima modelo,
        CancellationToken ct)
    {
        if (!ModelState.IsValid)
        {
            return ValidationProblem(ModelState);
        }


        bool existe = await db.ProductoMateriaPrima.AnyAsync(
            pm => pm.IdProducto == modelo.IdProducto &&
                  pm.IdMateriaPrima == modelo.IdMateriaPrima,
            ct);


        if (existe)
        {
            return Conflict(new
            {
                error = "Esta materia prima ya está asignada al producto."
            });
        }


        db.ProductoMateriaPrima.Add(modelo);

        await db.SaveChangesAsync(ct);

        return Ok(modelo);
    }


    // PUT: api/producto-materia-prima
    [HttpPut]
    public async Task<IActionResult> Update(
        [FromBody] ProductoMateriaPrima modelo,
        CancellationToken ct)
    {
        var existente = await db.ProductoMateriaPrima
            .FirstOrDefaultAsync(
                pm => pm.IdProducto == modelo.IdProducto &&
                      pm.IdMateriaPrima == modelo.IdMateriaPrima,
                ct);


        if (existente == null)
        {
            return NotFound(new
            {
                error = "La relación no existe."
            });
        }


        existente.Cantidad = modelo.Cantidad;

        await db.SaveChangesAsync(ct);

        return Ok(existente);
    }


    // DELETE: api/producto-materia-prima
    [HttpDelete]
    public async Task<IActionResult> Delete(
        int idProducto,
        int idMateriaPrima,
        CancellationToken ct)
    {
        var existente = await db.ProductoMateriaPrima
            .FirstOrDefaultAsync(
                pm => pm.IdProducto == idProducto &&
                      pm.IdMateriaPrima == idMateriaPrima,
                ct);


        if (existente == null)
        {
            return NotFound(new
            {
                error = "La relación no existe."
            });
        }


        db.ProductoMateriaPrima.Remove(existente);

        await db.SaveChangesAsync(ct);

        return NoContent();
    }
}