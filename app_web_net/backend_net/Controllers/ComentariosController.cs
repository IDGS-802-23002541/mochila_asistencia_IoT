using System;
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
[Route("api/comentarios")]
[Produces("application/json")]
public class ComentariosController(CangureraDbContext db) : ControllerBase
{
    // GET: api/comentarios
    [HttpGet]
    public async Task<IActionResult> GetAll([FromQuery] string? estado, CancellationToken ct)
    {
        var query = db.Comentarios.AsNoTracking().AsQueryable();

        if (!string.IsNullOrWhiteSpace(estado))
        {
            query = query.Where(c => c.Estado == estado);
        }

        var comentarios = await query
            .OrderByDescending(c => c.FechaCreacion)
            .ToListAsync(ct);

        return Ok(comentarios.Select(ToResponse));
    }

    // GET: api/comentarios/{id}
    [HttpGet("{id:int}")]
    public async Task<IActionResult> GetById(int id, CancellationToken ct)
    {
        var comentario = await db.Comentarios
            .AsNoTracking()
            .FirstOrDefaultAsync(c => c.IdComentario == id, ct);

        if (comentario == null)
        {
            return NotFound(new
            {
                error = $"Comentario {id} no encontrado."
            });
        }

        return Ok(ToResponse(comentario));
    }

    // POST: api/comentarios
    [HttpPost]
    public async Task<IActionResult> Create(
        [FromBody] CrearComentarioDto dto,
        CancellationToken ct)
    {
        if (!ModelState.IsValid)
        {
            return ValidationProblem(ModelState);
        }

        var comentario = new Comentario
        {
            NombreCliente = dto.NombreCliente,
            CorreoCliente = dto.CorreoCliente,
            Mensaje = dto.Mensaje,
            FechaCreacion = DateTime.UtcNow,
            Estado = "Pendiente"
        };

        db.Comentarios.Add(comentario);
        await db.SaveChangesAsync(ct);

        return CreatedAtAction(
            nameof(GetById),
            new { id = comentario.IdComentario },
            new { idComentario = comentario.IdComentario });
    }

    // PUT: api/comentarios/{id}
    [HttpPut("{id:int}")]
    public async Task<IActionResult> Update(
        int id,
        [FromBody] ActualizarComentarioDto dto,
        CancellationToken ct)
    {
        if (!ModelState.IsValid)
        {
            return ValidationProblem(ModelState);
        }

        var comentario = await db.Comentarios
            .FirstOrDefaultAsync(c => c.IdComentario == id, ct);

        if (comentario == null)
        {
            return NotFound(new
            {
                error = $"Comentario {id} no encontrado."
            });
        }

        comentario.Estado = dto.Estado;
        comentario.RespuestaAdministrador = dto.RespuestaAdministrador;

        if (!string.IsNullOrWhiteSpace(dto.RespuestaAdministrador))
        {
            comentario.FechaRespuesta = DateTime.UtcNow;
        }

        await db.SaveChangesAsync(ct);

        return Ok(new { idComentario = comentario.IdComentario });
    }

    // DELETE: api/comentarios/{id}
    [HttpDelete("{id:int}")]
    public async Task<IActionResult> Delete(int id, CancellationToken ct)
    {
        var comentario = await db.Comentarios
            .FirstOrDefaultAsync(c => c.IdComentario == id, ct);

        if (comentario == null)
        {
            return NotFound(new
            {
                error = $"Comentario {id} no encontrado."
            });
        }

        db.Comentarios.Remove(comentario);

        try
        {
            await db.SaveChangesAsync(ct);
        }
        catch (DbUpdateException)
        {
            return Conflict(new
            {
                error = "No se puede eliminar el comentario porque tiene relaciones asociadas."
            });
        }

        return NoContent();
    }

    private static object ToResponse(Comentario comentario)
    {
        return new ComentarioResponseDto
        {
            IdComentario = comentario.IdComentario,
            NombreCliente = comentario.NombreCliente,
            CorreoCliente = comentario.CorreoCliente,
            Mensaje = comentario.Mensaje,
            Estado = comentario.Estado,
            RespuestaAdministrador = comentario.RespuestaAdministrador,
            FechaCreacion = comentario.FechaCreacion,
            FechaRespuesta = comentario.FechaRespuesta
        };
    }
}