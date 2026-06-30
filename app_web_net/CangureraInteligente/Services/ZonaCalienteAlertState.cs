using System.Collections.Concurrent;

namespace CangureraInteligente.Services;

public class ZonaCalienteAlertState
{
    private readonly ConcurrentDictionary<int, HashSet<int>> _zonasPorDispositivo = new();

    public bool YaAlertado(int dispositivoId, int zonaId) =>
        _zonasPorDispositivo.TryGetValue(dispositivoId, out var zonas) && zonas.Contains(zonaId);

    public void ActualizarZonasActuales(int dispositivoId, IEnumerable<int> zonasDentroAhora) =>
        _zonasPorDispositivo[dispositivoId] = new HashSet<int>(zonasDentroAhora);
}