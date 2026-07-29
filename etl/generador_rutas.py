"""
generador_rutas.py
Generador de rutas simuladas realistas para VisionGuard, basado en los
andadores/calles reales del campus UTL (extraídos de mapa_utl.geojson).

Reutilizable para:
  - Mock de datos del ETL (Eventos_Detectados / RecorridoCoordenadas)
  - Simulación de coordenadas para la app Android (pendiente, mismo generador)
"""

import json
import random
from datetime import datetime, timedelta

def cargar_red_caminos(path_geojson):
    """
    Extrae únicamente las LineStrings transitables (footway/service) del geojson.
    Regresa una lista de rutas, cada una como lista de (lon, lat).
    """
    with open(path_geojson, encoding='utf-8') as f:
        data = json.load(f)

    caminos = []
    for feat in data['features']:
        geom = feat['geometry']
        props = feat.get('properties', {})
        if geom['type'] == 'LineString' and props.get('highway') in ('footway', 'service'):
            caminos.append(geom['coordinates'])  # [[lon, lat], [lon, lat], ...]

    print(f"Caminos transitables encontrados: {len(caminos)}")
    return caminos


def _interpolar_puntos(camino, num_puntos):
    """Genera num_puntos equiespaciados a lo largo de un camino (lon, lat)."""
    if len(camino) < 2 or num_puntos < 2:
        return camino

    # Distancia acumulada aproximada (en grados, suficiente para interpolar orden relativo)
    distancias = [0.0]
    for i in range(1, len(camino)):
        dx = camino[i][0] - camino[i-1][0]
        dy = camino[i][1] - camino[i-1][1]
        distancias.append(distancias[-1] + (dx**2 + dy**2) ** 0.5)

    total = distancias[-1]
    puntos = []
    for k in range(num_puntos):
        objetivo = total * k / (num_puntos - 1)
        for i in range(1, len(distancias)):
            if distancias[i] >= objetivo:
                t = (objetivo - distancias[i-1]) / (distancias[i] - distancias[i-1] + 1e-9)
                lon = camino[i-1][0] + t * (camino[i][0] - camino[i-1][0])
                lat = camino[i-1][1] + t * (camino[i][1] - camino[i-1][1])
                puntos.append((lon, lat))
                break
        else:
            puntos.append(camino[-1])
    return puntos


def generar_recorrido_simulado(caminos, num_puntos=10, fecha_inicio=None,
                                intervalo_s=30, jitter_gps=0.00002, seed=None):
    """
    Simula un recorrido completo (secuencia de coordenadas con timestamp),
    eligiendo un camino real del campus y muestreando puntos a lo largo de él.

    - jitter_gps: ruido pequeño para simular imprecisión real de GPS (NEO-6M).
    - Regresa lista de dicts: {"lat", "lon", "timestamp"}
    """
    rng = random.Random(seed)
    camino = rng.choice(caminos)
    puntos = _interpolar_puntos(camino, num_puntos)

    if fecha_inicio is None:
        from datetime import timezone
        fecha_inicio = datetime.now(timezone.utc)

    recorrido = []
    for i, (lon, lat) in enumerate(puntos):
        lat_ruido = lat + rng.uniform(-jitter_gps, jitter_gps)
        lon_ruido = lon + rng.uniform(-jitter_gps, jitter_gps)
        recorrido.append({
            "lat": round(lat_ruido, 6),
            "lon": round(lon_ruido, 6),
            "timestamp": fecha_inicio + timedelta(seconds=i * intervalo_s)
        })
    return recorrido


if __name__ == "__main__":
    caminos = cargar_red_caminos("mapa_utl.geojson")
    recorrido = generar_recorrido_simulado(caminos, num_puntos=8, seed=42)
    for p in recorrido:
        print(p)