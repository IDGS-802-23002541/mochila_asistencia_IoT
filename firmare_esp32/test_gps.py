# =============================================================================
# PROYECTO   : Vision Guard — Sistema de Navegación Aumentada
# ARCHIVO    : test_gps.py
# VERSIÓN    : 1.0
# =============================================================================
#
# INSTRUCCIONES:
#   Modo offline: ejecutar en cualquier PC o ESP32.
#       Estas pruebas no necesitan el módulo GPS conectado.
#   Modo online:  ejecutar en la ESP32 con el NEO-6M conectado.
#       Desactivar TEST_SOLO_OFFLINE = False
# =============================================================================

import time

# ─ Cambiar a False para probar con hardware real ─────────────────────────────
TEST_SOLO_OFFLINE = False

# ─ Importar con manejo de error para poder correr en PC ──────────────────────
try:
    from gps_manager import GPSManager
    GPS_DISPONIBLE = True
except ImportError:
    print("[ADVERTENCIA] gps_manager.py no encontrado. Solo pruebas de parseo.")
    GPS_DISPONIBLE = False


# ─────────────────────────────────────────────────────────────────────────────
# Utilidad de impresión
# ─────────────────────────────────────────────────────────────────────────────
def resultado(nombre, condicion, detalle=""):
    etiq = "[OK]   " if condicion else "[FALLO]"
    print(f"  {etiq} {nombre}", end="")
    if detalle:
        print(f" — {detalle}", end="")
    print()
    return condicion


# ─────────────────────────────────────────────────────────────────────────────
# PRUEBAS DE PARSEO NMEA (offline, no requiere hardware)
# ─────────────────────────────────────────────────────────────────────────────

# Sentencias NMEA reales (capturadas del carrito SmartCap en León, Gto.)
GPGGA_VALIDA = "$GPGGA,192315.00,2106.5517,N,10137.6464,W,1,08,0.9,1782.1,M,-27.4,M,,*6B"
GPRMC_VALIDA = "$GPRMC,192315.00,A,2106.5517,N,10137.6464,W,0.5,87.3,130525,,,A*60"
GNRMC_VALIDA = "$GNRMC,192316.00,A,2106.5520,N,10137.6461,W,1.2,90.0,130525,,,A*4F"
GPGGA_SIN_FIX = "$GPGGA,192315.00,,,,,,0,00,99.9,,M,,M,,*48"
SENTENCIA_INVALIDA = "$GPVTG,87.3,T,,M,0.5,N,0.9,K,A*35"
CHECKSUM_MALO = "$GPRMC,192315.00,A,2106.5517,N,10137.6464,W,0.5,87.3,130525,,,A*FF"

# Coordenadas esperadas (León, Guanajuato)
LAT_ESPERADA = 21.109195   # ±0.0001
LON_ESPERADA = -101.627440  # ±0.0001


def prueba_parseo_gpgga():
    """Verifica que GPGGA válida actualiza lat/lon/altitud/satélites."""
    print("\n[TEST 1] Parseo GPGGA válida")

    if not GPS_DISPONIBLE:
        resultado("GPS importado", False, "gps_manager.py no encontrado")
        return None

    gps = GPSManager(lat_defecto=0.0, lon_defecto=0.0)
    # Inyectar directamente al parser interno (sin UART)
    ok = gps._parsear_sentencia(GPGGA_VALIDA)

    resultado("_parsear_sentencia devuelve True", ok)
    resultado("tiene_fix es True", gps.tiene_fix)
    resultado("fix_quality == 1", gps.fix_quality == 1, f"obtenido={gps.fix_quality}")

    lat_ok = abs(gps.latitud - LAT_ESPERADA) < 0.001
    lon_ok = abs(gps.longitud - LON_ESPERADA) < 0.001
    resultado("Latitud correcta (León, Gto.)",  lat_ok,  f"{gps.latitud:.6f}")
    resultado("Longitud correcta (León, Gto.)", lon_ok, f"{gps.longitud:.6f}")
    resultado("Altitud > 0", gps.altitud > 0, f"{gps.altitud} m")
    resultado("Satélites == 8", gps.num_satelites == 8, f"sats={gps.num_satelites}")
    return gps


def prueba_parseo_gprmc():
    """Verifica que GPRMC válida actualiza velocidad y rumbo."""
    print("\n[TEST 2] Parseo GPRMC válida")
    if not GPS_DISPONIBLE:
        return

    gps = GPSManager(lat_defecto=0.0, lon_defecto=0.0)
    ok = gps._parsear_sentencia(GPRMC_VALIDA)

    resultado("_parsear_sentencia devuelve True", ok)
    resultado("tiene_fix es True", gps.tiene_fix)

    lat_ok = abs(gps.latitud - LAT_ESPERADA) < 0.001
    lon_ok = abs(gps.longitud - LON_ESPERADA) < 0.001
    resultado("Latitud correcta", lat_ok, f"{gps.latitud:.6f}")
    resultado("Longitud correcta", lon_ok, f"{gps.longitud:.6f}")

    vel_ok = abs(gps.velocidad_kmh - 0.5 * 1.852) < 0.01
    resultado("Velocidad correcta (0.5 kn → km/h)", vel_ok, f"{gps.velocidad_kmh:.3f} km/h")
    resultado("Rumbo correcto (87.3°)", abs(gps.rumbo - 87.3) < 0.1, f"{gps.rumbo}°")


def prueba_parseo_gnrmc():
    """Verifica soporte de receptores multi-constelación (GNRMC)."""
    print("\n[TEST 3] Parseo GNRMC (multi-constelación)")
    if not GPS_DISPONIBLE:
        return

    gps = GPSManager(lat_defecto=0.0, lon_defecto=0.0)
    ok = gps._parsear_sentencia(GNRMC_VALIDA)

    resultado("GNRMC reconocida y parseada", ok)
    resultado("tiene_fix es True", gps.tiene_fix)


def prueba_sin_fix():
    """Verifica que GPGGA con fix=0 no actualiza la posición."""
    print("\n[TEST 4] GPGGA sin fix (fix=0)")
    if not GPS_DISPONIBLE:
        return

    gps = GPSManager(lat_defecto=99.0, lon_defecto=99.0)
    ok = gps._parsear_sentencia(GPGGA_SIN_FIX)

    resultado("Parser devuelve False para fix=0", not ok)
    resultado("tiene_fix sigue False", not gps.tiene_fix)
    resultado("Latitud conserva defecto (99.0)", gps.latitud == 99.0, f"{gps.latitud}")


def prueba_sentencia_desconocida():
    """Verifica que sentencias no soportadas se ignoran silenciosamente."""
    print("\n[TEST 5] Sentencia NMEA no soportada (GPVTG)")
    if not GPS_DISPONIBLE:
        return

    gps = GPSManager(lat_defecto=0.0, lon_defecto=0.0)
    ok = gps._parsear_sentencia(SENTENCIA_INVALIDA)
    resultado("Parser devuelve False para GPVTG", not ok)
    resultado("tiene_fix sigue False", not gps.tiene_fix)


def prueba_checksum_malo():
    """Verifica que sentencias con checksum incorrecto se descartan."""
    print("\n[TEST 6] Checksum inválido")
    if not GPS_DISPONIBLE:
        return

    gps = GPSManager(lat_defecto=0.0, lon_defecto=0.0)
    ok = gps._parsear_sentencia(CHECKSUM_MALO)
    resultado("Sentencia con checksum *FF descartada", not ok,
              "Si es True, el checksum no se está verificando")


def prueba_conversion_nmea():
    """Prueba unitaria del método _nmea_a_decimal() de forma aislada."""
    print("\n[TEST 7] Conversión NMEA → decimal (_nmea_a_decimal)")
    if not GPS_DISPONIBLE:
        return

    # 2106.5517 N → 21 + 6.5517/60 = 21.109195
    lat = GPSManager._nmea_a_decimal("2106.5517", "N")
    resultado("Latitud Norte correcta",
              lat is not None and abs(lat - 21.109195) < 0.0001,
              f"obtenido={lat}")

    # Latitud Sur debe ser negativa
    lat_s = GPSManager._nmea_a_decimal("2106.5517", "S")
    resultado("Latitud Sur es negativa", lat_s is not None and lat_s < 0, f"{lat_s}")

    # Longitud Oeste debe ser negativa
    lon_w = GPSManager._nmea_a_decimal("10137.6464", "W")
    resultado("Longitud Oeste es negativa", lon_w is not None and lon_w < 0, f"{lon_w}")

    # Valor vacío → None
    ninguno = GPSManager._nmea_a_decimal("", "N")
    resultado("Cadena vacía → None", ninguno is None)


def prueba_historial():
    """Verifica que el historial circular funciona correctamente."""
    print("\n[TEST 8] Historial de posiciones (max=3)")
    if not GPS_DISPONIBLE:
        return

    gps = GPSManager(lat_defecto=0.0, lon_defecto=0.0, max_historial=3)

    # Inyectar 4 posiciones (la primera debe desaparecer)
    sentencias = [
        "$GPRMC,100000,A,2106.0000,N,10137.0000,W,0,0,130525,,,A*7B",
        "$GPRMC,100001,A,2106.1000,N,10137.1000,W,0,0,130525,,,A*78",
        "$GPRMC,100002,A,2106.2000,N,10137.2000,W,0,0,130525,,,A*79",
        "$GPRMC,100003,A,2106.3000,N,10137.3000,W,0,0,130525,,,A*78",
    ]
    # Nota: los checksums anteriores son placeholders; el parser acepta
    # sentencias sin checksum o con checksum truncado en modo permisivo.
    for s in sentencias:
        # Parsear sin validación de checksum (omitir el * final)
        partes = s.split(',')
        tipo = partes[0].upper()
        if tipo == '$GPRMC' and len(partes) > 8:
            try:
                lat = GPSManager._nmea_a_decimal(partes[3], partes[4])
                lon = GPSManager._nmea_a_decimal(partes[5], partes[6])
                if lat and lon:
                    gps._lat = lat
                    gps._lon = lon
                    gps._tiene_fix = True
                    gps._agregar_historial(lat, lon)
            except Exception:
                pass

    hist = gps.historial
    resultado("Historial no supera max=3", len(hist) <= 3, f"tamaño={len(hist)}")
    resultado("Historial tiene exactamente 3 entradas", len(hist) == 3)
    resultado("Cada entrada tiene clave 'lat'", all('lat' in e for e in hist))
    resultado("Cada entrada tiene clave 'lon'", all('lon' in e for e in hist))
    resultado("Cada entrada tiene clave 'ts'",  all('ts'  in e for e in hist))


def prueba_obtener_posicion():
    """Verifica la estructura del dict devuelto por obtener_posicion()."""
    print("\n[TEST 9] obtener_posicion() — estructura del diccionario")
    if not GPS_DISPONIBLE:
        return

    gps = GPSManager()
    gps._parsear_sentencia(GPGGA_VALIDA)
    pos = gps.obtener_posicion()

    claves = ["lat", "lon", "alt", "vel_kmh", "rumbo", "sats", "fix", "valido", "ts"]
    resultado("Dict tiene todas las claves", all(k in pos for k in claves),
              f"presentes={list(pos.keys())}")
    resultado("'valido' es bool", isinstance(pos["valido"], bool))
    resultado("'ts' es int",      isinstance(pos["ts"], int))
    resultado("'lat' es float",   isinstance(pos["lat"], float))


def prueba_json():
    """Verifica que obtener_posicion_json() produce JSON válido."""
    print("\n[TEST 10] obtener_posicion_json() — string JSON válido")
    if not GPS_DISPONIBLE:
        return

    import json
    gps = GPSManager()
    gps._parsear_sentencia(GPRMC_VALIDA)
    cadena = gps.obtener_posicion_json()

    try:
        obj = json.loads(cadena)
        resultado("JSON parseable sin excepción", True)
        resultado("JSON tiene clave 'lat'", "lat" in obj)
        resultado("JSON tiene clave 'lon'", "lon" in obj)
    except Exception as e:
        resultado("JSON parseable sin excepción", False, str(e))


# ─────────────────────────────────────────────────────────────────────────────
# PRUEBA ONLINE — requiere hardware GPS conectado
# ─────────────────────────────────────────────────────────────────────────────
async def prueba_online_fix():
    """
    Prueba con hardware real: espera un fix GPS durante 60 segundos.
    Solo ejecutar si TEST_SOLO_OFFLINE = False y el módulo está conectado.
    """
    print("\n[TEST ONLINE] Esperando fix GPS real (30 s máx)")
    import uasyncio as asyncio

    gps = GPSManager(uart_id=2, pin_tx=17, pin_rx=16)
    fix_ok = await gps.esperar_fix(timeout_s=30)

    resultado("Fix GPS obtenido antes del timeout", fix_ok)
    if fix_ok:
        pos = gps.obtener_posicion()
        resultado("Latitud en rango México (14-32°N)", 14 < pos["lat"] < 32, f"{pos['lat']:.6f}")
        resultado("Longitud en rango México (-118 a -86°W)", -118 < pos["lon"] < -86, f"{pos['lon']:.6f}")
        resultado("Al menos 4 satélites", pos["sats"] >= 4, f"{pos['sats']} sats")
        print(f"  → Posición: {pos['lat']:.6f}, {pos['lon']:.6f} | Alt: {pos['alt']} m | "
              f"Vel: {pos['vel_kmh']:.1f} km/h | Sats: {pos['sats']}")


# ─────────────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────────────
def main():
    print("=" * 55)
    print("  Vision Guard — TEST SUITE GPS")
    print("=" * 55)

    prueba_parseo_gpgga()
    prueba_parseo_gprmc()
    prueba_parseo_gnrmc()
    prueba_sin_fix()
    prueba_sentencia_desconocida()
    prueba_checksum_malo()
    prueba_conversion_nmea()
    prueba_historial()
    prueba_obtener_posicion()
    prueba_json()

    if not TEST_SOLO_OFFLINE and GPS_DISPONIBLE:
        import uasyncio as asyncio
        asyncio.run(prueba_online_fix())

    print("\n" + "=" * 55)
    print("  FIN — Revisa los [FALLO] antes de continuar con E2.")
    print("=" * 55)


main()

