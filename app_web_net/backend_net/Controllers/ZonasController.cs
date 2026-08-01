using CangureraInteligente.Data;
using CangureraInteligente.Models;
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using System.Threading.Tasks;

namespace CangureraInteligente.Controllers
{
    [ApiController]
    [Route("api/zonas")]
    public class ZonasController : ControllerBase
    {
        private readonly CangureraDbContext _context;

        public ZonasController(CangureraDbContext context)
        {
            _context = context;
        }

        // GET api/zonas/accesibilidad
        // Regresa el JSON completo de cada zona (contrato ZonaAccesibilidad),
        // ya armado por el pipeline Python (DBSCAN + IAZ) y guardado en
        // Analitico.Zonas_IAZ.DatosJson -- el backend no recalcula nada,
        // solo lee y sirve tal cual.
        [HttpGet("accesibilidad")]
        public async Task<IActionResult> GetZonasAccesibilidad()
        {
            var filas = await _context.Database
                .SqlQuery<string>($"SELECT DatosJson FROM Analitico.Zonas_IAZ WHERE DatosJson IS NOT NULL")
                .ToListAsync();

            // Cada fila ya es un JSON valido (string) -- los unimos en un
            // arreglo JSON sin pasar por deserializar/reserializar en C#.
            var arregloJson = "[" + string.Join(",", filas) + "]";
            return Content(arregloJson, "application/json");
        }
    }
}
