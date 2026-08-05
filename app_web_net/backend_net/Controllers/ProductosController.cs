using System.Linq;
using System.Threading;
using System.Threading.Tasks;
using CangureraInteligente.Data;
using CangureraInteligente.Models;
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;

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


    // POST: api/productos
    [HttpPost]
    public async Task<IActionResult> Create(
        [FromBody] Producto producto,
        CancellationToken ct)
    {
        if (!ModelState.IsValid)
        {
            return ValidationProblem(ModelState);
        }


        producto.IdProducto = 0;


        db.Productos.Add(producto);

        await db.SaveChangesAsync(ct);


        return CreatedAtAction(
            nameof(GetById),
            new
            {
                id = producto.IdProducto
            },
            producto);
    }


    // PUT: api/productos/{id}
    [HttpPut("{id:int}")]
    public async Task<IActionResult> Update(
        int id,
        [FromBody] Producto producto,
        CancellationToken ct)
    {
        if (id != producto.IdProducto &&
            producto.IdProducto != 0)
        {
            return BadRequest(new
            {
                error = "El id de la URL y el cuerpo no coinciden."
            });
        }


        var existente = await db.Productos
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


        existente.Nombre = producto.Nombre;
        existente.Descripcion = producto.Descripcion;
        existente.Precio = producto.Precio;
        existente.Stock = producto.Stock;
        existente.Activo = producto.Activo;


        await db.SaveChangesAsync(ct);


        return Ok(existente);
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