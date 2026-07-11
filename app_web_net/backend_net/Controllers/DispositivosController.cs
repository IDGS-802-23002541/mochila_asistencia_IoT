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
[Route("api/dispositivos")]
[Produces("application/json", new string[] { })]
public class DispositivosController(CangureraDbContext db) : ControllerBase
{
	[HttpGet]
	public async Task<IActionResult> GetAll([FromQuery] int? organizacionId, CancellationToken ct)
	{
		IQueryable<Dispositivo> query = db.Dispositivos.AsNoTracking().Include((Dispositivo d) => d.Organizacion);
		if (organizacionId.HasValue)
		{
			if (!(await db.Organizaciones.AnyAsync((Organizacion o) => o.Id == ((int?)organizacionId).Value, ct)))
			{
				return NotFound(new
				{
					error = $"La organización {organizacionId.Value} no existe."
				});
			}
			query = query.Where((Dispositivo d) => d.OrganizacionId == ((int?)organizacionId).Value);
		}
		return Ok(await (from d in query
			orderby d.Id
			select new
			{
				Id = d.Id,
				OrganizacionId = d.OrganizacionId,
				MacAddress = d.MacAddress,
				Estado = d.Estado,
				UltimaConexion = d.UltimaConexion,
				FechaRegistro = d.FechaRegistro,
				Organizacion = d.Organizacion.Nombre
			}).ToListAsync(ct));
	}

	[HttpGet("{id:int}")]
	public async Task<IActionResult> GetById(int id, CancellationToken ct)
	{
		Dispositivo dispositivo = await db.Dispositivos.AsNoTracking().Include((Dispositivo d) => d.Organizacion).FirstOrDefaultAsync((Dispositivo d) => d.Id == id, ct);
		IActionResult result;
		if (dispositivo != null)
		{
			IActionResult actionResult = Ok(dispositivo);
			result = actionResult;
		}
		else
		{
			IActionResult actionResult = NotFound(new
			{
				error = $"Dispositivo {id} no encontrado."
			});
			result = actionResult;
		}
		return result;
	}

	[HttpPost]
	public async Task<IActionResult> Create([FromBody] Dispositivo dispositivo, CancellationToken ct)
	{
		if (!base.ModelState.IsValid)
		{
			return ValidationProblem(base.ModelState);
		}
		if (!(await db.Organizaciones.AnyAsync((Organizacion o) => o.Id == dispositivo.OrganizacionId, ct)))
		{
			return BadRequest(new
			{
				error = $"No existe la organización {dispositivo.OrganizacionId}."
			});
		}
		if (await db.Dispositivos.AnyAsync((Dispositivo d) => d.MacAddress == dispositivo.MacAddress, ct))
		{
			return Conflict(new
			{
				error = "La MAC '" + dispositivo.MacAddress + "' ya está registrada."
			});
		}
		dispositivo.Id = 0;
		dispositivo.FechaRegistro = ((dispositivo.FechaRegistro == default(DateTime)) ? DateTime.UtcNow : dispositivo.FechaRegistro);
		db.Dispositivos.Add(dispositivo);
		await db.SaveChangesAsync(ct);
		return CreatedAtAction("GetById", new
		{
			id = dispositivo.Id
		}, dispositivo);
	}

	[HttpPut("{id:int}")]
	public async Task<IActionResult> Update(int id, [FromBody] Dispositivo dispositivo, CancellationToken ct)
	{
		if (id != dispositivo.Id && dispositivo.Id != 0)
		{
			return BadRequest(new
			{
				error = "El id de la URL y el cuerpo no coinciden."
			});
		}
		Dispositivo existing = await db.Dispositivos.FirstOrDefaultAsync((Dispositivo d) => d.Id == id, ct);
		if (existing == null)
		{
			return NotFound(new
			{
				error = $"Dispositivo {id} no encontrado."
			});
		}
		if (!(await db.Organizaciones.AnyAsync((Organizacion o) => o.Id == dispositivo.OrganizacionId, ct)))
		{
			return BadRequest(new
			{
				error = $"No existe la organización {dispositivo.OrganizacionId}."
			});
		}
		if (await db.Dispositivos.AnyAsync((Dispositivo d) => d.MacAddress == dispositivo.MacAddress && d.Id != id, ct))
		{
			return Conflict(new
			{
				error = "La MAC '" + dispositivo.MacAddress + "' ya está registrada."
			});
		}
		existing.OrganizacionId = dispositivo.OrganizacionId;
		existing.MacAddress = dispositivo.MacAddress;
		existing.Estado = dispositivo.Estado;
		existing.UltimaConexion = dispositivo.UltimaConexion;
		await db.SaveChangesAsync(ct);
		return Ok(existing);
	}

	[HttpDelete("{id:int}")]
	public async Task<IActionResult> Delete(int id, CancellationToken ct)
	{
		Dispositivo dispositivo = await db.Dispositivos.FirstOrDefaultAsync((Dispositivo d) => d.Id == id, ct);
		if (dispositivo == null)
		{
			return NotFound(new
			{
				error = $"Dispositivo {id} no encontrado."
			});
		}
		db.Dispositivos.Remove(dispositivo);
		try
		{
			await db.SaveChangesAsync(ct);
		}
		catch (DbUpdateException)
		{
			return Conflict(new
			{
				error = "No se puede eliminar el dispositivo porque tiene recorridos asociados."
			});
		}
		return NoContent();
	}
}
