using System.Linq;
using System.Threading;
using System.Threading.Tasks;
using CangureraInteligente.Data;
using CangureraInteligente.Models;
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;

namespace CangureraInteligente.Controllers;

[ApiController]
[Route("api/proveedores")]
[Produces("application/json")]
public class ProveedoresController(CangureraDbContext db) : ControllerBase
{
    // GET: api/proveedores
    [HttpGet]
    public async Task<IActionResult> GetAll(CancellationToken ct)
    {
        var proveedores = await (
            from p in db.Proveedores.AsNoTracking()
            orderby p.IdProveedor
            select p
        ).ToListAsync(ct);

        return Ok(proveedores);
    }


    // GET: api/proveedores/{id}
    [HttpGet("{id:int}")]
    public async Task<IActionResult> GetById(int id, CancellationToken ct)
    {
        var proveedor = await db.Proveedores
            .AsNoTracking()
            .FirstOrDefaultAsync(
                p => p.IdProveedor == id,
                ct);

        if (proveedor == null)
        {
            return NotFound(new
            {
                error = $"Proveedor {id} no encontrado."
            });
        }

        return Ok(proveedor);
    }


    // POST: api/proveedores
    [HttpPost]
    public async Task<IActionResult> Create(
        [FromBody] Proveedor proveedor,
        CancellationToken ct)
    {
        if (!ModelState.IsValid)
        {
            return ValidationProblem(ModelState);
        }

        proveedor.IdProveedor = 0;

        db.Proveedores.Add(proveedor);

        await db.SaveChangesAsync(ct);

        return CreatedAtAction(
            nameof(GetById),
            new
            {
                id = proveedor.IdProveedor
            },
            proveedor);
    }


    // PUT: api/proveedores/{id}
    [HttpPut("{id:int}")]
    public async Task<IActionResult> Update(
        int id,
        [FromBody] Proveedor proveedor,
        CancellationToken ct)
    {
        if (id != proveedor.IdProveedor &&
            proveedor.IdProveedor != 0)
        {
            return BadRequest(new
            {
                error = "El id de la URL y el cuerpo no coinciden."
            });
        }


        var existente = await db.Proveedores
            .FirstOrDefaultAsync(
                p => p.IdProveedor == id,
                ct);


        if (existente == null)
        {
            return NotFound(new
            {
                error = $"Proveedor {id} no encontrado."
            });
        }


        existente.Nombre = proveedor.Nombre;
        existente.Telefono = proveedor.Telefono;
        existente.Correo = proveedor.Correo;
        existente.Direccion = proveedor.Direccion;
        existente.Activo = proveedor.Activo;


        await db.SaveChangesAsync(ct);

        return Ok(existente);
    }


    // DELETE: api/proveedores/{id}
    [HttpDelete("{id:int}")]
    public async Task<IActionResult> Delete(
        int id,
        CancellationToken ct)
    {
        var proveedor = await db.Proveedores
            .FirstOrDefaultAsync(
                p => p.IdProveedor == id,
                ct);


        if (proveedor == null)
        {
            return NotFound(new
            {
                error = $"Proveedor {id} no encontrado."
            });
        }


        db.Proveedores.Remove(proveedor);

        try
        {
            await db.SaveChangesAsync(ct);
        }
        catch (DbUpdateException)
        {
            return Conflict(new
            {
                error = "No se puede eliminar el proveedor porque tiene materias primas asociadas."
            });
        }


        return NoContent();
    }
}