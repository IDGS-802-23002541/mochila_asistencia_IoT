# ============================================================
# Generador de datos mock v6 - VisionGuard
# Version corregida: se agrega la celda que faltaba (construccion real
# de GRAFO_CAMPUS), y se elimina la funcion generar_sql_insercion
# duplicada (la vieja de v5 sobreescribia a la nueva).
#
# Copia cada bloque "# --- CELDA N ---" a su propia celda de Jupyter,
# en este mismo orden. No te saltes ninguna.
# ============================================================

# --- CELDA 0 ---
import math
import random
from datetime import datetime, timedelta
import networkx as nx
from generador_rutas import cargar_red_caminos
import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))


print("Librerias importadas.")


# --- CELDA 1 ---
PUNTOS_INTERES = {
    "Entrada A (autos/motos)": (21.063707015763327, -101.58608800705031),
    "Canchas Americano": (21.063814358104942, -101.585052751258),
    "Canchas Basquet": (21.064720801456563, -101.58408779061212),
    "Canchas Futbol": (21.06337902479519, -101.58378104815513),
    "Edificio B Pesado": (21.064325327866044, -101.58327763915618),
    "Edificio B": (21.064188168664696, -101.58254912582085),
    "Edificio A": (21.063347320362, -101.58254273535302),
    "Edificio C": (21.063955594077722, -101.58179505061413),
    "Edificio A Pesado": (21.06287620469662, -101.58212096447465),
    "Entrada A Principal (peatonal)": (21.06271344521116, -101.58172754292714),
    "Biblioteca": (21.063031255581514, -101.58123907989197),
    "Cafeteria": (21.062828496692823, -101.58073423293152),
    "Edificio D": (21.063633567121133, -101.58048500468523),
    "Edificio CVD": (21.062673445591482, -101.58028690018176),
    "Cajeros ATM": (21.06302543762953, -101.58052265942663),
    "Edificio E / SITO": (21.063383101232517, -101.57965424386425),
    "Edificio F": (21.06321016024924, -101.5791493968933),
    "Edificio Rectoria": (21.062693442356547, -101.57857565396391),
    "Estacionamiento": (21.062162248378776, -101.57865327544415),
    "Entrada C (estacionamiento)": (21.061751779006062, -101.57839453717669),
}

# Puntos de riesgo v6 -- levantados a mano por Damian via Google Maps,
# cada uno con su tipo de evento fijo (ya no se sortea al azar como en v5).
PUNTOS_DE_RIESGO = {
    "Ramas bajas (frente Edificio C)": (21.063607931905043, -101.58126982406363),
    "Camellon sin pavimentar (entrada-parking)": (21.062331521719084, -101.57817296773752),
    "Banqueta levantada (CVD-Cafeteria)": (21.062962504622387, -101.58048550588111),
    "Banqueta levantada (esquina Biblioteca)": (21.06333073079787, -101.58156591571392),
    "Camellon sin podotactil (atras esquina Biblioteca)": (21.062936393781236, -101.58158428837176),
    "Banqueta sin rampa (entrada peatonal principal)": (21.063363718466682, -101.58191943010623),
}

# Cada punto SIEMPRE genera su propio tipo de evento -- decision v6,
# reemplaza el sorteo global (DISTRIBUCION_EVENTOS) usado en v5.
TIPO_EVENTO_POR_PUNTO = {
    "Ramas bajas (frente Edificio C)": 2,                                  # Obstaculo / Baja
    "Camellon sin pavimentar (entrada-parking)": 5,                        # Tropiezo / Media
    "Banqueta levantada (CVD-Cafeteria)": 5,                               # Tropiezo / Media
    "Banqueta levantada (esquina Biblioteca)": 5,                          # Tropiezo / Media
    "Camellon sin podotactil (atras esquina Biblioteca)": 4,               # Caida_Detectada / Critica
    "Banqueta sin rampa (entrada peatonal principal)": 5,                  # Tropiezo / Media
}

print(f"Puntos de interés: {len(PUNTOS_INTERES)} | Puntos de riesgo v6: {len(PUNTOS_DE_RIESGO)}")


# --- CELDA 2 (funciones del grafo, UNA sola definicion de cada funcion) ---
def _distancia_m(lat1, lon1, lat2, lon2):
    R = 6371000
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2)**2
    return 2 * R * math.asin(math.sqrt(a))

def construir_grafo_base(caminos):
    G = nx.Graph()
    for camino in caminos:
        nodos_camino = [(round(lat, 7), round(lon, 7)) for lon, lat in camino]
        for i in range(len(nodos_camino) - 1):
            n1, n2 = nodos_camino[i], nodos_camino[i + 1]
            G.add_edge(n1, n2, weight=_distancia_m(n1[0], n1[1], n2[0], n2[1]))
    print(f"Grafo base: {G.number_of_nodes()} nodos, {G.number_of_edges()} aristas")
    return G

def conectar_componentes_cercanos(G, distancia_max_m=8):
    componentes = list(nx.connected_components(G))
    print(f"Componentes antes de conectar: {len(componentes)}")
    conexiones = 0
    for i in range(len(componentes)):
        for j in range(i + 1, len(componentes)):
            mejor_par = None
            mejor_dist = float("inf")
            for n1 in componentes[i]:
                for n2 in componentes[j]:
                    d = _distancia_m(n1[0], n1[1], n2[0], n2[1])
                    if d < mejor_dist:
                        mejor_dist = d
                        mejor_par = (n1, n2)
            if mejor_par and mejor_dist <= distancia_max_m:
                G.add_edge(mejor_par[0], mejor_par[1], weight=mejor_dist)
                conexiones += 1
    print(f"Conexiones agregadas: {conexiones}")
    print(f"Componentes después de conectar: {nx.number_connected_components(G)}")
    return G

def es_nodo_camino(n):
    return isinstance(n, tuple) and len(n) == 2 and n[0] != "POI"

def nodo_mas_cercano(G, lat, lon):
    mejor_nodo, mejor_dist = None, float("inf")
    for nodo in G.nodes:
        if not es_nodo_camino(nodo):
            continue
        d = _distancia_m(lat, lon, nodo[0], nodo[1])
        if d < mejor_dist:
            mejor_dist, mejor_nodo = d, nodo
    return mejor_nodo, mejor_dist

def agregar_nodos_de_acceso(G, puntos):
    for nombre, (lat, lon) in puntos.items():
        nodo_punto = ("POI", nombre)
        nodo_cercano, dist = nodo_mas_cercano(G, lat, lon)
        G.add_node(nodo_punto, lat=lat, lon=lon)
        G.add_edge(nodo_punto, nodo_cercano, weight=dist, tipo="acceso")
    return G

def coords_de_nodo(G, n):
    if isinstance(n, tuple) and n[0] == "POI":
        d = G.nodes[n]
        return d["lat"], d["lon"]
    return n[0], n[1]

def generar_ruta_con_nombre(G, nombre_origen, nombre_destino):
    # Ruta mas corta (Dijkstra) entre 2 puntos con nombre (POI o riesgo)
    no, nd = ("POI", nombre_origen), ("POI", nombre_destino)
    camino_nodos = nx.shortest_path(G, no, nd, weight="weight")
    return [coords_de_nodo(G, n) for n in camino_nodos]

print("Funciones del grafo definidas.")


# --- CELDA 3 (ESTA ES LA QUE FALTABA -- construye GRAFO_CAMPUS de verdad) ---
CAMINOS = cargar_red_caminos("mapa_utl.geojson")
GRAFO_CAMPUS = construir_grafo_base(CAMINOS)
GRAFO_CAMPUS = conectar_componentes_cercanos(GRAFO_CAMPUS, distancia_max_m=8)
GRAFO_CAMPUS = agregar_nodos_de_acceso(GRAFO_CAMPUS, PUNTOS_INTERES)
GRAFO_CAMPUS = agregar_nodos_de_acceso(GRAFO_CAMPUS, PUNTOS_DE_RIESGO)
print(f"Grafo ampliado: {GRAFO_CAMPUS.number_of_nodes()} nodos, "
      f"{nx.number_connected_components(GRAFO_CAMPUS)} componente(s)")


# --- CELDA 4 (generacion del mock) ---
random.seed(42)

FECHA_INICIO_RANGO = datetime(2026, 7, 1)
DIAS_RANGO = 15
DISPOSITIVO_ID = 10
HORA_MIN = 16   # 4:00 pm
HORA_MAX = 21   # 9:00 pm

PARES_RUTA = [
    ("Edificio C", "Biblioteca", ["Ramas bajas (frente Edificio C)"]),
    ("Entrada C (estacionamiento)", "Estacionamiento", ["Camellon sin pavimentar (entrada-parking)"]),
    ("Edificio CVD", "Cafeteria", ["Banqueta levantada (CVD-Cafeteria)"]),
    ("Entrada A Principal (peatonal)", "Biblioteca", [
        "Banqueta levantada (esquina Biblioteca)",
        "Camellon sin podotactil (atras esquina Biblioteca)",
    ]),
    ("Entrada A Principal (peatonal)", "Edificio A", ["Banqueta sin rampa (entrada peatonal principal)"]),
]

RECORRIDOS_POR_PAR = [3 if len(p[2]) == 1 else 3 * len(p[2]) for p in PARES_RUTA]
N_TOTAL_RECORRIDOS = sum(RECORRIDOS_POR_PAR)

def generar_recorrido_dirigido(origen, destino, seed, fecha_base, jitter_gps=0.00002, intervalo_s=30):
    rng = random.Random(seed)
    nodos_ruta = generar_ruta_con_nombre(GRAFO_CAMPUS, origen, destino)
    recorrido = []
    for i, (lat, lon) in enumerate(nodos_ruta):
        lat_r = lat + rng.uniform(-jitter_gps, jitter_gps)
        lon_r = lon + rng.uniform(-jitter_gps, jitter_gps)
        recorrido.append({
            "lat": round(lat_r, 6),
            "lon": round(lon_r, 6),
            "timestamp": fecha_base + timedelta(seconds=i * intervalo_s),
        })
    return recorrido

def generar_mock_completo():
    recorridos = []
    eventos = []
    rid = 0
    idx_dia = 0

    for (origen, destino, puntos_riesgo), n_rec in zip(PARES_RUTA, RECORRIDOS_POR_PAR):
        for _ in range(n_rec):
            rid += 1
            dia_offset = idx_dia % DIAS_RANGO
            idx_dia += 1
            hora_random = random.randint(HORA_MIN * 60, HORA_MAX * 60)
            fecha_base = FECHA_INICIO_RANGO.replace(hour=0, minute=0, second=0) + \
                         timedelta(days=dia_offset, minutes=hora_random)

            ruta = generar_recorrido_dirigido(origen, destino, seed=rid, fecha_base=fecha_base)
            recorridos.append({"recorrido_id": rid, "coordenadas": ruta})

            n_eventos = random.randint(2, 4)
            for k in range(n_eventos):
                nombre_riesgo = puntos_riesgo[k % len(puntos_riesgo)]
                lat_r, lon_r = PUNTOS_DE_RIESGO[nombre_riesgo]
                lat_jitter = lat_r + random.uniform(-0.00005, 0.00005)
                lon_jitter = lon_r + random.uniform(-0.00005, 0.00005)

                punto_base = random.choice(ruta)
                timestamp_evento = punto_base["timestamp"] + timedelta(seconds=random.randint(-15, 15))
                ts_min, ts_max = ruta[0]["timestamp"], ruta[-1]["timestamp"]
                timestamp_evento = max(ts_min, min(ts_max, timestamp_evento))

                eventos.append({
                    "recorrido_id": rid,
                    "tipo_evento_id": TIPO_EVENTO_POR_PUNTO[nombre_riesgo],
                    "latitud": lat_jitter,
                    "longitud": lon_jitter,
                    "geo_es_estimado": False,
                    "timestamp": timestamp_evento,
                })

    print(f"Mock v6 generado: {len(recorridos)} recorridos, {len(eventos)} eventos, "
          f"dispositivo unico Id {DISPOSITIVO_ID}, rango {FECHA_INICIO_RANGO.date()} a "
          f"{(FECHA_INICIO_RANGO + timedelta(days=DIAS_RANGO-1)).date()}.")
    return recorridos, eventos

recorridos_mock, eventos_mock = generar_mock_completo()


# --- CELDA 5 (exportar SQL para produccion -- UNICA definicion) ---
def generar_sql_insercion(recorridos, eventos, nombre_archivo="insercion_mock_v6_prod.sql"):
    lines = []
    lines.append("-- Mock v6 -- puntos reales de riesgo, dispositivo unico Id 10")
    lines.append("-- Rango simulado: 1-15 julio 2026. Insercion ADITIVA, no borra nada.")
    lines.append("")
    for rec in recorridos:
        rid = rec["recorrido_id"]
        coords = rec["coordenadas"]
        fecha_inicio_r = coords[0]["timestamp"].strftime("%Y-%m-%d %H:%M:%S")
        fecha_fin_r = coords[-1]["timestamp"].strftime("%Y-%m-%d %H:%M:%S")

        lines.append(f"-- Recorrido mock v6 #{rid} (DispositivoId {DISPOSITIVO_ID})")
        lines.append("DECLARE @NewId TABLE (Id BIGINT);")
        lines.append("INSERT INTO Operativo.Recorridos (DispositivoId, FechaInicio, FechaFin, Ruta_Coordenadas)")
        lines.append("OUTPUT INSERTED.Id INTO @NewId")
        lines.append(f"VALUES ({DISPOSITIVO_ID}, '{fecha_inicio_r}', '{fecha_fin_r}', NULL);")
        lines.append("")
        lines.append("DECLARE @RecId BIGINT = (SELECT TOP 1 Id FROM @NewId);")
        lines.append("")
        for c in coords:
            fecha = c["timestamp"].strftime("%Y-%m-%d %H:%M:%S")
            lines.append(
                f"INSERT INTO Operativo.RecorridoCoordenadas (RecorridoId, Fecha, Latitud, Longitud) "
                f"VALUES (@RecId, '{fecha}', {c['lat']}, {c['lon']});"
            )
        lines.append("")
        eventos_rec = [e for e in eventos if e["recorrido_id"] == rid]
        for e in eventos_rec:
            ts = e["timestamp"].strftime("%Y-%m-%d %H:%M:%S")
            geo_est = 0 if not e["geo_es_estimado"] else 1
            lines.append(
                f"INSERT INTO Operativo.Eventos_Detectados "
                f"(RecorridoId, TipoEventoId, TimestampEvento, Latitud, Longitud, Geo_Es_Estimado) "
                f"VALUES (@RecId, {e['tipo_evento_id']}, '{ts}', {round(e['latitud'],6)}, {round(e['longitud'],6)}, {geo_est});"
            )
        lines.append("GO")
        lines.append("")

    lines.append("-- Verificacion")
    lines.append("SELECT COUNT(*) AS TotalRecorridos FROM Operativo.Recorridos;")
    lines.append("SELECT COUNT(*) AS TotalCoordenadas FROM Operativo.RecorridoCoordenadas;")
    lines.append("SELECT COUNT(*) AS TotalEventos FROM Operativo.Eventos_Detectados;")

    with open(nombre_archivo, "w") as f:
        f.write("\n".join(lines))
    print(f"Script generado: {nombre_archivo}")

generar_sql_insercion(recorridos_mock, eventos_mock)


