using System.Threading;
using System.Threading.Tasks;
using CangureraInteligente.Data;
using CangureraInteligente.DTOs;
using CangureraInteligente.Models;
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using System;
using System.Linq;

namespace CangureraInteligente.Controllers;

[ApiController]
[Route("api/ventas")]
[Produces("application/json")]
public class VentasController(CangureraDbContext db) : ControllerBase
{

    // GET
    [HttpGet]
    public async Task<IActionResult> GetAll(
        [FromQuery] int? organizacionId,
        CancellationToken ct)
    {
        var query = db.Ventas
            .AsNoTracking()
            .AsQueryable();

        if (organizacionId.HasValue)
        {
            query = query.Where(v => v.IdOrganizacion == organizacionId.Value);
        }

        var ventas = await query
            .OrderByDescending(v => v.FechaVenta)
            .Select(v => new VentaResponseDto
            {
                IdVenta = v.IdVenta,
                FechaVenta = v.FechaVenta,
                Total = v.Total,
                IdOrganizacion = v.IdOrganizacion,
                Detalles = v.Detalles!
                    .Select(d => new VentaItemDto
                    {
                        IdDetalleVenta = d.IdDetalleVenta,
                        IdVenta = d.IdVenta,
                        IdProducto = d.IdProducto,
                        Cantidad = d.Cantidad,
                        PrecioUnitario = d.PrecioUnitario,
                        Producto = d.Producto == null
                            ? null
                            : new ProductoVentaDto
                            {
                                IdProducto = d.Producto.IdProducto,
                                Nombre = d.Producto.Nombre,
                                FotoUrl = d.Producto.FotoUrl
                            }
                    })
                    .ToList()
            })
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
            .AsNoTracking()
            .Where(v => v.IdVenta == id)
            .Select(v => new VentaResponseDto
            {
                IdVenta = v.IdVenta,
                FechaVenta = v.FechaVenta,
                Total = v.Total,
                IdOrganizacion = v.IdOrganizacion,
                Detalles = v.Detalles!
                    .Select(d => new VentaItemDto
                    {
                        IdDetalleVenta = d.IdDetalleVenta,
                        IdVenta = d.IdVenta,
                        IdProducto = d.IdProducto,
                        Cantidad = d.Cantidad,
                        PrecioUnitario = d.PrecioUnitario,
                        Producto = d.Producto == null
                            ? null
                            : new ProductoVentaDto
                            {
                                IdProducto = d.Producto.IdProducto,
                                Nombre = d.Producto.Nombre,
                                FotoUrl = d.Producto.FotoUrl
                            }
                    })
                    .ToList()
            })
            .FirstOrDefaultAsync(ct);


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

        if (venta.IdOrganizacion <= 0)
        {
            return BadRequest(new
            {
                error = "La venta debe estar asociada a una organización."
            });
        }

        if (venta.Detalles == null || venta.Detalles.Count == 0)
        {
            return BadRequest(new
            {
                error = "La venta debe tener al menos un detalle."
            });
        }

        if (!await db.Organizaciones.AnyAsync(o => o.Id == venta.IdOrganizacion, ct))
        {
            return NotFound(new
            {
                error = $"Organización {venta.IdOrganizacion} no existe."
            });
        }

        venta.FechaVenta = DateTime.UtcNow;
        venta.Total = 0;

        foreach (var detalle in venta.Detalles!)
        {
            var producto = await db.Productos
                .FirstOrDefaultAsync(
                    p => p.IdProducto == detalle.IdProducto,
                    ct);

            if (producto == null)
            {
                return NotFound(new
                {
                    error = $"Producto {detalle.IdProducto} no existe."
                });
            }

            if (producto.Stock < detalle.Cantidad)
            {
                return BadRequest(new
                {
                    error = $"Stock insuficiente del producto {producto.Nombre}."
                });
            }

            // DESCUENTA INVENTARIO
            producto.Stock -= detalle.Cantidad;

            detalle.PrecioUnitario = producto.Precio;
            venta.Total += producto.Precio * detalle.Cantidad;
        }

        db.Ventas.Add(venta);

        await db.SaveChangesAsync(ct);

        return Ok(new
        {
            venta.IdVenta,
            venta.IdOrganizacion,
            venta.FechaVenta,
            venta.Total
        });
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