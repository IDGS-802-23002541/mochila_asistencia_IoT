using System;
using System.Linq;
using System.Security.Cryptography;
using System.Text;
using System.Threading;
using System.Threading.Tasks;
using CangureraInteligente.DTOs;
using CangureraInteligente.Data;
using CangureraInteligente.Models;
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;

namespace CangureraInteligente.Controllers;

[ApiController]
[Route("api/usuarios")]
[Produces("application/json", new string[] { })]
public class UsuariosController(CangureraDbContext db) : ControllerBase
{
	[HttpPost("login")]
	[ProducesResponseType(typeof(LoginResponse), 200)]
	[ProducesResponseType(401)]
	[ProducesResponseType(403)]
	public async Task<IActionResult> Login([FromBody] LoginRequest req, CancellationToken ct)
	{
		if (!base.ModelState.IsValid)
		{
			return ValidationProblem(base.ModelState);
		}
		string correo = req.Correo.Trim();
		Usuario usuario = await db.Usuarios.AsNoTracking().Include((Usuario u) => u.Organizacion).FirstOrDefaultAsync((Usuario u) => u.Correo.ToLower() == correo.ToLower(), ct);
		if (usuario != null && ValidarContrasena(req.Contrasena, usuario.Contrasena_Hash))
		{
			if (!usuario.Estado_Activo)
			{
				return StatusCode(403, new
				{
					error = "El usuario está inactivo."
				});
			}
			return Ok(new LoginResponse
			{
				Id = usuario.Id,
				Nombre = usuario.Nombre,
				Correo = usuario.Correo,
				Rol = usuario.Rol,
				OrganizacionId = usuario.OrganizacionId,
				Estado_Activo = usuario.Estado_Activo,
				Mensaje = "Login exitoso"
			});
		}

		Organizacion organizacion = await db.Organizaciones.AsNoTracking().FirstOrDefaultAsync((Organizacion o) => o.Email_Contacto != null && o.Email_Contacto.ToLower() == correo.ToLower(), ct);
		if (organizacion != null && !string.IsNullOrWhiteSpace(organizacion.Contrasena_Hash) && ValidarContrasena(req.Contrasena, organizacion.Contrasena_Hash))
		{
			if (!organizacion.Estado_Activo)
			{
				return StatusCode(403, new
				{
					error = "La organización está inactiva."
				});
			}
			return Ok(new LoginResponse
			{
				Id = organizacion.Id,
				Nombre = organizacion.Nombre,
				Correo = organizacion.Email_Contacto ?? string.Empty,
				Rol = organizacion.Rol,
				OrganizacionId = organizacion.Id,
				Estado_Activo = organizacion.Estado_Activo,
				Mensaje = "Login exitoso"
			});
		}

		return Unauthorized(new
		{
			error = "Correo o contraseña inválidos."
		});
	}

	[HttpGet]
	public async Task<IActionResult> GetAll(CancellationToken ct)
	{
		return Ok(await (from u in db.Usuarios.AsNoTracking().Include((Usuario u) => u.Organizacion)
			orderby u.Id
			select u).ToListAsync(ct));
	}

	[HttpGet("{id:int}")]
	public async Task<IActionResult> GetById(int id, CancellationToken ct)
	{
		Usuario usuario = await db.Usuarios.AsNoTracking().Include((Usuario u) => u.Organizacion).FirstOrDefaultAsync((Usuario u) => u.Id == id, ct);
		IActionResult result;
		if (usuario != null)
		{
			IActionResult actionResult = Ok(usuario);
			result = actionResult;
		}
		else
		{
			IActionResult actionResult = NotFound(new
			{
				error = $"Usuario {id} no encontrado."
			});
			result = actionResult;
		}
		return result;
	}

	[HttpPost]
	public async Task<IActionResult> Create([FromBody] Usuario usuario, CancellationToken ct)
	{
		if (!base.ModelState.IsValid)
		{
			return ValidationProblem(base.ModelState);
		}
		if (!(await db.Organizaciones.AnyAsync((Organizacion o) => o.Id == usuario.OrganizacionId, ct)))
		{
			return BadRequest(new
			{
				error = $"No existe la organización {usuario.OrganizacionId}."
			});
		}
		if (await db.Usuarios.AnyAsync((Usuario u) => u.Correo == usuario.Correo, ct))
		{
			return Conflict(new
			{
				error = "El correo '" + usuario.Correo + "' ya está registrado."
			});
		}
		usuario.Id = 0;
		usuario.FechaRegistro = ((usuario.FechaRegistro == default(DateTime)) ? DateTime.UtcNow : usuario.FechaRegistro);
		db.Usuarios.Add(usuario);
		await db.SaveChangesAsync(ct);
		return CreatedAtAction("GetById", new
		{
			id = usuario.Id
		}, usuario);
	}

	[HttpPut("{id:int}")]
	public async Task<IActionResult> Update(int id, [FromBody] Usuario usuario, CancellationToken ct)
	{
		if (id != usuario.Id && usuario.Id != 0)
		{
			return BadRequest(new
			{
				error = "El id de la URL y el cuerpo no coinciden."
			});
		}
		Usuario existing = await db.Usuarios.FirstOrDefaultAsync((Usuario u) => u.Id == id, ct);
		if (existing == null)
		{
			return NotFound(new
			{
				error = $"Usuario {id} no encontrado."
			});
		}
		if (!(await db.Organizaciones.AnyAsync((Organizacion o) => o.Id == usuario.OrganizacionId, ct)))
		{
			return BadRequest(new
			{
				error = $"No existe la organización {usuario.OrganizacionId}."
			});
		}
		if (await db.Usuarios.AnyAsync((Usuario u) => u.Correo == usuario.Correo && u.Id != id, ct))
		{
			return Conflict(new
			{
				error = "El correo '" + usuario.Correo + "' ya está registrado."
			});
		}
		existing.OrganizacionId = usuario.OrganizacionId;
		existing.Nombre = usuario.Nombre;
		existing.Correo = usuario.Correo;
		existing.Contrasena_Hash = usuario.Contrasena_Hash;
		existing.Rol = usuario.Rol;
		existing.Estado_Activo = usuario.Estado_Activo;
		await db.SaveChangesAsync(ct);
		return Ok(existing);
	}

	[HttpDelete("{id:int}")]
	public async Task<IActionResult> Delete(int id, CancellationToken ct)
	{
		Usuario usuario = await db.Usuarios.FirstOrDefaultAsync((Usuario u) => u.Id == id, ct);
		if (usuario == null)
		{
			return NotFound(new
			{
				error = $"Usuario {id} no encontrado."
			});
		}
		db.Usuarios.Remove(usuario);
		try
		{
			await db.SaveChangesAsync(ct);
		}
		catch (DbUpdateException)
		{
			return Conflict(new
			{
				error = "No se puede eliminar el usuario porque tiene dependencias asociadas."
			});
		}
		return NoContent();
	}

	private static bool ValidarContrasena(string contrasena, string contrasenaHash)
	{
		if (string.IsNullOrWhiteSpace(contrasena) || string.IsNullOrWhiteSpace(contrasenaHash))
		{
			return false;
		}
		if (!EsHashCriptograficoValido(contrasenaHash))
		{
			return false;
		}
		byte[] inArray = ((contrasenaHash.Length == 64) ? SHA256.HashData(Encoding.UTF8.GetBytes(contrasena)) : SHA512.HashData(Encoding.UTF8.GetBytes(contrasena)));
		return string.Equals(Convert.ToHexString(inArray), contrasenaHash, StringComparison.OrdinalIgnoreCase);
	}

	private static bool EsHashCriptograficoValido(string hash)
	{
		if (hash.Length == 64 || hash.Length == 128)
		{
			return hash.All((char c) => "0123456789abcdefABCDEF".Contains(c));
		}
		return false;
	}
}
