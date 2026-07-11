using System;
using System.Linq;
using System.Threading;
using System.Threading.Tasks;
using CangureraInteligente.Data;
using CangureraInteligente.Models;
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;

namespace CangureraInteligente.Controllers;

[ApiController]
[Route("api/organizaciones")]
[Produces("application/json", new string[] { })]
public class OrganizacionesController(CangureraDbContext db) : ControllerBase
{
	[HttpGet]
	public async Task<IActionResult> GetAll(CancellationToken ct)
	{
		return Ok(await (from o in db.Organizaciones.AsNoTracking()
			orderby o.Id
			select o).ToListAsync(ct));
	}

	[HttpGet("{id:int}")]
	public async Task<IActionResult> GetById(int id, CancellationToken ct)
	{
		Organizacion organizacion = await db.Organizaciones.AsNoTracking().FirstOrDefaultAsync((Organizacion o) => o.Id == id, ct);
		IActionResult result;
		if (organizacion != null)
		{
			IActionResult actionResult = Ok(organizacion);
			result = actionResult;
		}
		else
		{
			IActionResult actionResult = NotFound(new
			{
				error = $"Organización {id} no encontrada."
			});
			result = actionResult;
		}
		return result;
	}

	[HttpPost]
	public async Task<IActionResult> Create([FromBody] Organizacion organizacion, CancellationToken ct)
	{
		if (!base.ModelState.IsValid)
		{
			return ValidationProblem(base.ModelState);
		}
		organizacion.Id = 0;
		organizacion.FechaCreacion = ((organizacion.FechaCreacion == default(DateTime)) ? DateTime.UtcNow : organizacion.FechaCreacion);
		db.Organizaciones.Add(organizacion);
		await db.SaveChangesAsync(ct);
		return CreatedAtAction("GetById", new
		{
			id = organizacion.Id
		}, organizacion);
	}

	[HttpPut("{id:int}")]
	public async Task<IActionResult> Update(int id, [FromBody] Organizacion organizacion, CancellationToken ct)
	{
		if (id != organizacion.Id && organizacion.Id != 0)
		{
			return BadRequest(new
			{
				error = "El id de la URL y el cuerpo no coinciden."
			});
		}
		Organizacion existing = await db.Organizaciones.FirstOrDefaultAsync((Organizacion o) => o.Id == id, ct);
		if (existing == null)
		{
			return NotFound(new
			{
				error = $"Organización {id} no encontrada."
			});
		}
		existing.Nombre = organizacion.Nombre;
		existing.Sector = organizacion.Sector;
		existing.Contacto_Principal = organizacion.Contacto_Principal;
		existing.Email_Contacto = organizacion.Email_Contacto;
		existing.Estado_Activo = organizacion.Estado_Activo;
		existing.Contrasena_Hash = organizacion.Contrasena_Hash;
		existing.Rol = organizacion.Rol;
		existing.Es_Interna = organizacion.Es_Interna;
		await db.SaveChangesAsync(ct);
		return Ok(existing);
	}

	[HttpDelete("{id:int}")]
	public async Task<IActionResult> Delete(int id, CancellationToken ct)
	{
		Organizacion organizacion = await db.Organizaciones.FirstOrDefaultAsync((Organizacion o) => o.Id == id, ct);
		if (organizacion == null)
		{
			return NotFound(new
			{
				error = $"Organización {id} no encontrada."
			});
		}
		db.Organizaciones.Remove(organizacion);
		try
		{
			await db.SaveChangesAsync(ct);
		}
		catch (DbUpdateException)
		{
			return Conflict(new
			{
				error = "No se puede eliminar la organización porque tiene dependencias asociadas."
			});
		}
		return NoContent();
	}
}
