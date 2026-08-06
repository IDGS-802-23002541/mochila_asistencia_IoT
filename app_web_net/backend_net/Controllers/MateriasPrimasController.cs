using System.Linq;
using System.Threading;
using System.Threading.Tasks;
using CangureraInteligente.Data;
using CangureraInteligente.DTOs;
using CangureraInteligente.Models;
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;

namespace CangureraInteligente.Controllers;

[ApiController]
[Route("api/materias-primas")]
[Produces("application/json")]
public class MateriasPrimasController(CangureraDbContext db) : ControllerBase
{
    // GET: api/materias-primas
    [HttpGet]
    public async Task<IActionResult> GetAll(CancellationToken ct)
    {
        var materias = await db.MateriasPrimas
            .Include(m => m.Proveedor)
            .AsNoTracking()
            .OrderBy(m => m.IdMateriaPrima)
            .ToListAsync(ct);

        var respuesta = materias.Select(m =>
            new MateriaPrimaResponseDto
            {
                IdMateriaPrima = m.IdMateriaPrima,
                Nombre = m.Nombre,
                Descripcion = m.Descripcion,
                CostoUnitario = m.CostoUnitario,
                PrecioPromedio = PrecioPromedioCompra(m.IdMateriaPrima),
                Stock = m.Stock,
                StockMinimo = m.StockMinimo,
                IdProveedor = m.IdProveedor,
                Proveedor = ToProveedorResumen(m.Proveedor)
            });

        return Ok(respuesta);
    }


    // GET: api/materias-primas/{id}
    [HttpGet("{id:int}")]
    public async Task<IActionResult> GetById(int id, CancellationToken ct)
    {
        var materiaPrima = await db.MateriasPrimas
            .Include(m => m.Proveedor)
            .AsNoTracking()
            .FirstOrDefaultAsync(
                m => m.IdMateriaPrima == id,
                ct);


        if (materiaPrima == null)
        {
            return NotFound(new
            {
                error = $"Materia prima {id} no encontrada."
            });
        }

        var respuesta = new MateriaPrimaResponseDto
        {
            IdMateriaPrima = materiaPrima.IdMateriaPrima,
            Nombre = materiaPrima.Nombre,
            Descripcion = materiaPrima.Descripcion,
            CostoUnitario = materiaPrima.CostoUnitario,
            PrecioPromedio = PrecioPromedioCompra(materiaPrima.IdMateriaPrima),
            Stock = materiaPrima.Stock,
            StockMinimo = materiaPrima.StockMinimo,
            IdProveedor = materiaPrima.IdProveedor,
            Proveedor = ToProveedorResumen(materiaPrima.Proveedor)
        };

        return Ok(respuesta);
    }


    // POST: api/materias-primas
    [HttpPost]
    public async Task<IActionResult> Create(
        [FromBody] MateriaPrima materiaPrima,
        CancellationToken ct)
    {
        if (!ModelState.IsValid)
        {
            return ValidationProblem(ModelState);
        }


        materiaPrima.IdMateriaPrima = 0;


        db.MateriasPrimas.Add(materiaPrima);

        await db.SaveChangesAsync(ct);


        return CreatedAtAction(
            nameof(GetById),
            new
            {
                id = materiaPrima.IdMateriaPrima
            },
            materiaPrima);
    }


    // PUT: api/materias-primas/{id}
    [HttpPut("{id:int}")]
    public async Task<IActionResult> Update(
        int id,
        [FromBody] MateriaPrima materiaPrima,
        CancellationToken ct)
    {
        if (id != materiaPrima.IdMateriaPrima &&
            materiaPrima.IdMateriaPrima != 0)
        {
            return BadRequest(new
            {
                error = "El id de la URL y el cuerpo no coinciden."
            });
        }


        var existente = await db.MateriasPrimas
            .FirstOrDefaultAsync(
                m => m.IdMateriaPrima == id,
                ct);


        if (existente == null)
        {
            return NotFound(new
            {
                error = $"Materia prima {id} no encontrada."
            });
        }


        existente.Nombre = materiaPrima.Nombre;
        existente.Descripcion = materiaPrima.Descripcion;
        existente.CostoUnitario = materiaPrima.CostoUnitario;
        existente.Stock = materiaPrima.Stock;
        existente.StockMinimo = materiaPrima.StockMinimo;
        existente.IdProveedor = materiaPrima.IdProveedor;


        await db.SaveChangesAsync(ct);


        return Ok(existente);
    }


    // DELETE: api/materias-primas/{id}
    [HttpDelete("{id:int}")]
    public async Task<IActionResult> Delete(
        int id,
        CancellationToken ct)
    {
        var materiaPrima = await db.MateriasPrimas
            .FirstOrDefaultAsync(
                m => m.IdMateriaPrima == id,
                ct);


        if (materiaPrima == null)
        {
            return NotFound(new
            {
                error = $"Materia prima {id} no encontrada."
            });
        }


        db.MateriasPrimas.Remove(materiaPrima);


        try
        {
            await db.SaveChangesAsync(ct);
        }
        catch (DbUpdateException)
        {
            return Conflict(new
            {
                error = "No se puede eliminar la materia prima porque tiene registros relacionados."
            });
        }


        return NoContent();
    }

    // Promedio del precio de las últimas 5 compras de una materia prima.
    private decimal? PrecioPromedioCompra(int idMateriaPrima)
    {
        var ultimos = db.DetallesCompra
            .Where(d => d.IdMateriaPrima == idMateriaPrima)
            .OrderByDescending(d => d.Compra!.FechaCompra)
            .Take(5)
            .Select(d => d.PrecioUnitario)
            .ToList();

        return ultimos.Count == 0 ? null : ultimos.Average();
    }

    private static ProveedorResumenDto? ToProveedorResumen(Proveedor? proveedor)
    {
        if (proveedor == null)
        {
            return null;
        }

        return new ProveedorResumenDto
        {
            IdProveedor = proveedor.IdProveedor,
            Nombre = proveedor.Nombre
        };
    }
}