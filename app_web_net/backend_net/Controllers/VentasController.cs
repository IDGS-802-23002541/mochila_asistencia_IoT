using System.Threading;
using System.Threading.Tasks;
using CangureraInteligente.Data;
using CangureraInteligente.Models;
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using System;

namespace CangureraInteligente.Controllers;

[ApiController]
[Route("api/ventas")]
[Produces("application/json")]
public class VentasController(CangureraDbContext db) : ControllerBase
{

    // GET
    [HttpGet]
    public async Task<IActionResult> GetAll(CancellationToken ct)
    {
        var ventas = await db.Ventas
            .Include(v => v.Detalles)
            .ThenInclude(d => d.Producto)
            .AsNoTracking()
            .ToListAsync(ct);

        return Ok(ventas);
    }


    // GET BY ID
    [HttpGet("{id:int}")]
    public async Task<IActionResult> GetById(
        int id,
        CancellationToken ct)
    {
        var venta = await db.Ventas
            .Include(v => v.Detalles)
            .ThenInclude(d => d.Producto)
            .FirstOrDefaultAsync(
                v => v.IdVenta == id,
                ct);


        if (venta == null)
        {
            return NotFound(new
            {
                error = "Venta no encontrada."
            });
        }


        return Ok(venta);
    }



    // POST
    [HttpPost]
    public async Task<IActionResult> Create(
        Venta venta,
        CancellationToken ct)
    {
        if (!ModelState.IsValid)
        {
            return ValidationProblem(ModelState);
        }


        venta.FechaVenta = DateTime.UtcNow;


        foreach(var detalle in venta.Detalles!)
        {
            var producto = await db.Productos
                .FirstOrDefaultAsync(
                    p => p.IdProducto == detalle.IdProducto,
                    ct);


            if(producto == null)
            {
                return NotFound(new
                {
                    error = $"Producto {detalle.IdProducto} no existe."
                });
            }


            if(producto.Stock < detalle.Cantidad)
            {
                return BadRequest(new
                {
                    error = $"Stock insuficiente del producto {producto.Nombre}."
                });
            }


            // DESCUENTA INVENTARIO
            producto.Stock -= detalle.Cantidad;


            detalle.PrecioUnitario = producto.Precio;
        }



        db.Ventas.Add(venta);

        await db.SaveChangesAsync(ct);


        return Ok(venta);
    }



    // DELETE
    [HttpDelete("{id:int}")]
    public async Task<IActionResult> Delete(
        int id,
        CancellationToken ct)
    {
        var venta = await db.Ventas
            .FirstOrDefaultAsync(
                v => v.IdVenta == id,
                ct);


        if(venta == null)
        {
            return NotFound();
        }


        db.Ventas.Remove(venta);

        await db.SaveChangesAsync(ct);


        return NoContent();
    }
}