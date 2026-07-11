using System.Collections.Concurrent;
using System.Collections.Generic;

namespace CangureraInteligente.Services;

public class ZonaCalienteAlertState
{
	private readonly ConcurrentDictionary<int, HashSet<int>> _zonasPorDispositivo = new ConcurrentDictionary<int, HashSet<int>>();

	public bool YaAlertado(int dispositivoId, int zonaId)
	{
		if (_zonasPorDispositivo.TryGetValue(dispositivoId, out HashSet<int> value))
		{
			return value.Contains(zonaId);
		}
		return false;
	}

	public void ActualizarZonasActuales(int dispositivoId, IEnumerable<int> zonasDentroAhora)
	{
		_zonasPorDispositivo[dispositivoId] = new HashSet<int>(zonasDentroAhora);
	}
}
