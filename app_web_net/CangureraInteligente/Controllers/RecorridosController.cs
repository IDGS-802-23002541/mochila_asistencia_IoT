using CangureraInteligente.Data;
using CangureraInteligente.DTOs;
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;

namespace CangureraInteligente.Controllers;

/// <summary>
/// Endpoints HTTP consumidos por la app móvil (préstamo de mochila).
/// Base URL: /api/recorridos
/// </summary>
[ApiController]
[Route("api/recorridos")]
[Produces("application/json")]
public class RecorridosController(CangureraDbContext db, ILogger<RecorridosController> log)
    : ControllerBase
{
    // ──────────────────────────────────────────────────────────────────────
    // POST /api/recorridos/iniciar
    // Inicia el préstamo: crea un Recorrido y devuelve el ID al móvil.
    // El móvil luego envía ese ID al ESP32 vía Bluetooth.
    // ──────────────────────────────────────────────────────────────────────
    [HttpPost("iniciar")]
    [ProducesResponseType(typeof(IniciarRecorridoResponse), StatusCodes.Status201Created)]
    [ProducesResponseType(StatusCodes.Status400BadRequest)]
    [ProducesResponseType(StatusCodes.Status404NotFound)]
    [ProducesResponseType(StatusCodes.Status409Conflict)]
    public async Task<IActionResult> IniciarRecorrido(
        [FromBody] IniciarRecorridoRequest req,
        CancellationToken ct)
    {
        // 1. Buscar dispositivo por MAC
        var dispositivo = await db.Dispositivos
            .Include(d => d.Organizacion)
            .FirstOrDefaultAsync(d => d.MacAddress == req.DispositivoMac, ct);

        if (dispositivo is null)
            return NotFound(new { error = $"Dispositivo con MAC '{req.DispositivoMac}' no encontrado." });

        if (dispositivo.Estado != "Activo")
            return Conflict(new { error = $"El dispositivo '{req.DispositivoMac}' no está activo (estado: {dispositivo.Estado})." });

        // 2. Verificar que el dispositivo no tenga un recorrido en curso
        bool enUso = await db.Recorridos
            .AnyAsync(r => r.DispositivoId == dispositivo.Id && r.FechaFin == null, ct);

        if (enUso)
            return Conflict(new { error = "El dispositivo ya tiene un recorrido activo sin cerrar." });

        // 3. Validar discapacidad si se mandó
        if (req.DiscapacidadId.HasValue)
        {
            bool discapacidadExiste = await db.TiposDiscapacidad
                .AnyAsync(d => d.Id == req.DiscapacidadId.Value, ct);

            if (!discapacidadExiste)
                return BadRequest(new { error = $"DiscapacidadId {req.DiscapacidadId} no existe en el catálogo." });
        }

        // 4. Crear recorrido
        var recorrido = new Models.Recorrido
        {
            DispositivoId  = dispositivo.Id,
            FechaInicio    = DateTime.UtcNow,
            Usuario_Edad   = req.UsuarioEdad,
            DiscapacidadId = req.DiscapacidadId
        };

        db.Recorridos.Add(recorrido);

        // 5. Actualizar UltimaConexion del dispositivo
        dispositivo.UltimaConexion = DateTime.UtcNow;

        await db.SaveChangesAsync(ct);

        log.LogInformation(
            "Recorrido {RecorridoId} iniciado para dispositivo {Mac} (Org: {Org})",
            recorrido.Id, dispositivo.MacAddress, dispositivo.Organizacion.Nombre);

        return CreatedAtAction(nameof(GetRecorrido), new { id = recorrido.Id },
            new IniciarRecorridoResponse
            {
                RecorridoId    = recorrido.Id,
                DispositivoMac = dispositivo.MacAddress,
                FechaInicio    = recorrido.FechaInicio
            });
    }

    // ──────────────────────────────────────────────────────────────────────
    // GET /api/recorridos/{id}
    // Consulta el estado de un recorrido (útil para el móvil y para debug).
    // ──────────────────────────────────────────────────────────────────────
    [HttpGet("{id:int}")]
    [ProducesResponseType(typeof(RecorridoDetalleResponse), StatusCodes.Status200OK)]
    [ProducesResponseType(StatusCodes.Status404NotFound)]
    public async Task<IActionResult> GetRecorrido(int id, CancellationToken ct)
    {
        var recorrido = await db.Recorridos
            .Include(r => r.Dispositivo).ThenInclude(d => d.Organizacion)
            .Include(r => r.Discapacidad)
            .Include(r => r.Eventos)
            .FirstOrDefaultAsync(r => r.Id == id, ct);

        if (recorrido is null)
            return NotFound(new { error = $"Recorrido {id} no encontrado." });

        return Ok(new RecorridoDetalleResponse
        {
            Id             = recorrido.Id,
            DispositivoMac = recorrido.Dispositivo.MacAddress,
            Organizacion   = recorrido.Dispositivo.Organizacion.Nombre,
            FechaInicio    = recorrido.FechaInicio,
            FechaFin       = recorrido.FechaFin,
            UsuarioEdad    = recorrido.Usuario_Edad,
            Discapacidad   = recorrido.Discapacidad?.Nombre,
            TotalEventos   = recorrido.Eventos.Count
        });
    }

    // ──────────────────────────────────────────────────────────────────────
    // GET /api/recorridos/catalogos/discapacidades
    // Catálogo de discapacidades para el picker del móvil.
    // ──────────────────────────────────────────────────────────────────────
    [HttpGet("catalogos/discapacidades")]
    [ProducesResponseType(StatusCodes.Status200OK)]
    public async Task<IActionResult> GetDiscapacidades(CancellationToken ct)
    {
        var lista = await db.TiposDiscapacidad
            .Select(d => new { d.Id, d.Nombre })
            .ToListAsync(ct);

        return Ok(lista);
    }

    // ──────────────────────────────────────────────────────────────────────
    // GET /api/recorridos/catalogos/eventos
    // Catálogo de tipos de evento para referencia del ESP32.
    // ──────────────────────────────────────────────────────────────────────
    [HttpGet("catalogos/eventos")]
    [ProducesResponseType(StatusCodes.Status200OK)]
    public async Task<IActionResult> GetTiposEvento(CancellationToken ct)
    {
        var lista = await db.TiposEvento
            .Select(e => new { e.Id, e.NombreEvento, e.Severidad })
            .ToListAsync(ct);

        return Ok(lista);
    }
}