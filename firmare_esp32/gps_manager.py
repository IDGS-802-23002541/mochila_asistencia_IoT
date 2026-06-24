# =============================================================================
# PROYECTO   : Vision Guard
# ARCHIVO    : gps_manager.py
# DESCRIPCIÓN: Clase GPSManager — encapsula la lectura del módulo GPS
#              Ublox NEO-6M (o compatible NMEA-0183) via UART.
#
#              MEJORAS RESPECTO AL ORIGINAL:
#                - Encapsulado en clase (sin variables globales)
#                - Parseo extendido: GPGGA, GPRMC y GNRMC (u-blox modernos)
#                - Calidad de señal: campo fix_quality (0=sin señal, 1=GPS, 2=DGPS)
#                - Altitud extraída de GPGGA
#                - Velocidad y rumbo extraídos de GPRMC
#                - Historial circular de últimas N posiciones (para traza de ruta)
#                - Método esta_fijo() para saber si la señal es válida
#                - Publicación MQTT automática cada N segundos
# VERSIÓN    : 1.0
# =============================================================================

from machine import UART, Pin
import uasyncio as asyncio
import time
import json
import gc


class GPSManager:
    """
    Gestor del módulo GPS Ublox NEO-6M para Safe-Path AI.

    Parsea sentencias NMEA-0183 (GPGGA, GPRMC, GNRMC) recibidas por UART
    y expone latitud, longitud, altitud, velocidad y calidad de señal.

    Parámetros de constructor:
        uart_id    (int)  : ID del periférico UART (0, 1 o 2)     — default 2
        pin_tx     (int)  : GPIO TX del ESP32 → RX del GPS         — default 17
        pin_rx     (int)  : GPIO RX del ESP32 ← TX del GPS         — default 16
        baudrate   (int)  : velocidad serial del módulo GPS         — default 9600
        lat_defecto(float): latitud usada si no hay señal GPS       — default 21.1092
        lon_defecto(float): longitud usada si no hay señal GPS      — default -101.6275
        max_historial(int): tamaño del historial de posiciones      — default 10

    NOTA DE HARDWARE:
        El NEO-6M usa UART a 9600 bps por defecto.
        Conectar: GPS-TX → ESP32-RX (pin_rx), GPS-RX → ESP32-TX (pin_tx).
        El módulo necesita ~30 s para obtener fix en frío (primera vez).
        En interiores puede no obtener fix; usar lat/lon de defecto como fallback.

    NOTA PEDAGOGICA — NMEA-0183:
        Los módulos GPS envían continuamente sentencias de texto que empiezan
        con '$'. Las más importantes son:
          $GPGGA → posición, altitud, calidad, satélites
          $GPRMC → posición, velocidad, rumbo, fecha/hora
          $GNRMC → igual que GPRMC pero para receptores multi-constelación
        Cada campo está separado por coma. Los grados decimales se calculan:
          decimal = grados_enteros + minutos / 60
    """

    # ── Valores centinela para "sin dato" ──────────────────────────────────
    SIN_DATO = None

    def __init__(self,
                 uart_id=2,
                 pin_tx=17, pin_rx=16,
                 baudrate=9600,
                 lat_defecto=21.1092,
                 lon_defecto=-101.6275,
                 max_historial=10):

        # Inicializar UART
        try:
            self._uart = UART(uart_id,
                              baudrate=baudrate,
                              tx=Pin(pin_tx),
                              rx=Pin(pin_rx))
            self._uart_ok = True
            print(f"[GPSManager] UART{uart_id} inicializado (TX={pin_tx}, RX={pin_rx}, {baudrate} bps)")
        except Exception as e:
            print(f"[GPSManager] Error al inicializar UART: {e}")
            self._uart = None
            self._uart_ok = False

        # Estado GPS
        self._lat          = lat_defecto
        self._lon          = lon_defecto
        self._altitud      = 0.0
        self._velocidad_kn = 0.0   # nudos
        self._rumbo        = 0.0   # grados respecto al norte
        self._fix_quality  = 0     # 0=sin fix, 1=GPS, 2=DGPS
        self._num_sats     = 0     # satélites visibles
        self._tiene_fix    = False
        self._ts_ultimo    = 0     # timestamp UNIX del último fix válido

        # Fallback — coordenadas cuando no hay señal
        self._lat_defecto  = lat_defecto
        self._lon_defecto  = lon_defecto

        # Historial circular de posiciones [(lat, lon, ts), ...]
        self._max_historial = max_historial
        self._historial     = []

        # Buffer para acumular bytes UART (líneas incompletas)
        self._buffer        = ""

    # ─────────────────────────────────────────────────────────────────────
    # PARSEO NMEA — privado
    # ─────────────────────────────────────────────────────────────────────

    @staticmethod
    def _nmea_a_decimal(valor_nmea, direccion):
        """
        Convierte coordenada en formato NMEA (DDDMM.MMMM) a decimal.

        Ejemplo NMEA:  2106.5517  N
        Resultado:     21 + 6.5517/60 = 21.10919...
        """
        if not valor_nmea:
            return None
        try:
            valor = float(valor_nmea)
            grados = int(valor / 100)
            minutos = valor - grados * 100
            decimal = grados + minutos / 60.0
            if direccion in ('S', 'W'):
                decimal = -decimal
            return decimal
        except (ValueError, TypeError):
            return None

    def _parsear_gpgga(self, partes):
        """
        Parsea sentencia GPGGA.
        Formato: $GPGGA,hhmmss.ss,lat,N/S,lon,E/W,fix,sats,hdop,alt,M,...

        Campos útiles:
            partes[2] = latitud NMEA
            partes[3] = N/S
            partes[4] = longitud NMEA
            partes[5] = E/W
            partes[6] = fix quality (0=sin fix, 1=GPS, 2=DGPS)
            partes[7] = número de satélites
            partes[9] = altitud en metros
        """
        if len(partes) < 10:
            return False

        lat = self._nmea_a_decimal(partes[2], partes[3])
        lon = self._nmea_a_decimal(partes[4], partes[5])

        if lat is None or lon is None:
            return False

        try:
            fix = int(partes[6]) if partes[6] else 0
            sats = int(partes[7]) if partes[7] else 0
            alt = float(partes[9]) if partes[9] else 0.0
        except (ValueError, IndexError):
            fix, sats, alt = 0, 0, 0.0

        if fix > 0:
            self._lat         = lat
            self._lon         = lon
            self._altitud     = alt
            self._fix_quality = fix
            self._num_sats    = sats
            self._tiene_fix   = True
            self._ts_ultimo   = int(time.time())
            self._agregar_historial(lat, lon)
            return True
        return False

    def _parsear_gprmc(self, partes):
        """
        Parsea sentencia GPRMC (o GNRMC).
        Formato: $GPRMC,hhmmss,A/V,lat,N/S,lon,E/W,velocidad_kn,rumbo,fecha,...

        Campos útiles:
            partes[2] = A (activo/válido) o V (inválido)
            partes[3] = latitud NMEA
            partes[4] = N/S
            partes[5] = longitud NMEA
            partes[6] = E/W
            partes[7] = velocidad en nudos
            partes[8] = rumbo en grados (respecto al norte verdadero)
        """
        if len(partes) < 8:
            return False

        if partes[2] != 'A':   # 'V' = datos inválidos
            return False

        lat = self._nmea_a_decimal(partes[3], partes[4])
        lon = self._nmea_a_decimal(partes[5], partes[6])

        if lat is None or lon is None:
            return False

        try:
            vel = float(partes[7]) if partes[7] else 0.0
            rum = float(partes[8]) if partes[8] else 0.0
        except (ValueError, IndexError):
            vel, rum = 0.0, 0.0

        self._lat            = lat
        self._lon            = lon
        self._velocidad_kn   = vel
        self._rumbo          = rum
        self._tiene_fix      = True
        self._ts_ultimo      = int(time.time())
        self._agregar_historial(lat, lon)
        return True

    def _parsear_sentencia(self, linea):
        """
        Dispatcher: determina el tipo de sentencia NMEA y llama al parser
        correspondiente. Soporta GPGGA, GPRMC y GNRMC.

        Devuelve True si se actualizó la posición.
        """
        linea = linea.strip()
        if not linea.startswith('$'):
            return False

        # Verificar checksum si está presente (formato: ...*HH)
        if '*' in linea:
            datos, checksum_str = linea[1:].rsplit('*', 1)
            checksum_calc = 0
            for c in datos:
                checksum_calc ^= ord(c)
            try:
                if checksum_calc != int(checksum_str[:2], 16):
                    return False   # checksum inválido — descartar
            except ValueError:
                pass  # si no se puede leer el checksum, continuar

        partes = linea.split(',')
        tipo = partes[0].upper()

        if tipo in ('$GPGGA', '$GNGGA'):
            return self._parsear_gpgga(partes)
        elif tipo in ('$GPRMC', '$GNRMC'):
            return self._parsear_gprmc(partes)
        return False

    # ─────────────────────────────────────────────────────────────────────
    # HISTORIAL DE POSICIONES
    # ─────────────────────────────────────────────────────────────────────

    def _agregar_historial(self, lat, lon):
        """Agrega una posición al historial circular."""
        entrada = {"lat": lat, "lon": lon, "ts": int(time.time())}
        if len(self._historial) >= self._max_historial:
            self._historial.pop(0)
        self._historial.append(entrada)

    @property
    def historial(self):
        """
        Lista de las últimas N posiciones, más antigua primero.
        Cada elemento: {"lat": float, "lon": float, "ts": int}
        """
        return list(self._historial)

    # ─────────────────────────────────────────────────────────────────────
    # LECTURA UART — público
    # ─────────────────────────────────────────────────────────────────────

    def leer_uart(self):
        """
        Lee bytes disponibles en el UART sin bloquear.
        Acumula en buffer interno y parsea cuando encuentra fin de línea.
        Debe llamarse frecuentemente (desde una corutina asyncio).

        Devuelve: True si se actualizó la posición en esta llamada.
        """
        if not self._uart_ok or self._uart is None:
            return False

        actualizado = False
        try:
            while self._uart.any():
                byte = self._uart.read(1)
                if byte:
                    caracter = byte.decode('utf-8', 'ignore')
                    if caracter == '\n':
                        if self._buffer:
                            if self._parsear_sentencia(self._buffer):
                                actualizado = True
                            self._buffer = ""
                    elif caracter != '\r':
                        self._buffer += caracter
                        # Protección: evitar buffer infinito si no llega '\n'
                        if len(self._buffer) > 120:
                            self._buffer = ""
        except Exception as e:
            print(f"[GPSManager] Error leyendo UART: {e}")
            self._buffer = ""

        return actualizado

    async def esperar_fix(self, timeout_s=60):
        """
        Espera activamente hasta obtener un fix GPS válido.
        Útil al inicio del programa para enviar posición inicial a Firebase.

        Parámetro:
            timeout_s (int): segundos máximos de espera — default 60

        Devuelve: True si obtuvo fix, False si se agotó el tiempo.

        """
        if not self._uart_ok:
            print("[GPSManager] UART no disponible. Usando coordenadas de defecto.")
            return False

        print(f"[GPSManager] Esperando fix GPS (timeout={timeout_s}s)...")
        inicio = time.time()

        while time.time() - inicio < timeout_s:
            if self.leer_uart() and self._tiene_fix:
                print(f"[GPSManager] Fix obtenido: {self._lat:.6f}, {self._lon:.6f}")
                return True
            await asyncio.sleep(1)

        print(f"[GPSManager] Timeout sin fix. Usando defecto: {self._lat_defecto}, {self._lon_defecto}")
        return False

    # ─────────────────────────────────────────────────────────────────────
    # PROPIEDADES DE ACCESO — público
    # ─────────────────────────────────────────────────────────────────────

    @property
    def latitud(self):
        """Latitud decimal actual. Si no hay fix, devuelve la de defecto."""
        return self._lat

    @property
    def longitud(self):
        """Longitud decimal actual. Si no hay fix, devuelve la de defecto."""
        return self._lon

    @property
    def altitud(self):
        """Altitud en metros sobre el nivel del mar (solo disponible con GPGGA)."""
        return self._altitud

    @property
    def velocidad_kmh(self):
        """Velocidad en km/h (convertida de nudos: 1 kn = 1.852 km/h)."""
        return self._velocidad_kn * 1.852

    @property
    def rumbo(self):
        """Rumbo en grados respecto al norte verdadero (0–360)."""
        return self._rumbo

    @property
    def num_satelites(self):
        """Número de satélites GPS visibles en el último fix."""
        return self._num_sats

    @property
    def fix_quality(self):
        """Calidad del fix: 0=sin señal, 1=GPS estándar, 2=DGPS."""
        return self._fix_quality

    @property
    def tiene_fix(self):
        """True si se ha obtenido al menos un fix GPS válido."""
        return self._tiene_fix

    def esta_fijo(self, max_antiguedad_s=30):
        """
        Devuelve True si el último fix es válido y reciente.

        Parámetro:
            max_antiguedad_s (int): segundos máximos desde el último fix.

        Uso recomendado antes de publicar coordenadas en MQTT o Firebase.
        """
        if not self._tiene_fix:
            return False
        return (int(time.time()) - self._ts_ultimo) <= max_antiguedad_s

    def obtener_posicion(self):
        """
        Devuelve un diccionario con la posición y metadatos actuales.

        Estructura:
        {
            "lat"      : float,
            "lon"      : float,
            "alt"      : float,
            "vel_kmh"  : float,
            "rumbo"    : float,
            "sats"     : int,
            "fix"      : int,       # 0=sin señal, 1=GPS, 2=DGPS
            "valido"   : bool,      # True si fix reciente
            "ts"       : int        # timestamp UNIX
        }
        """
        return {
            "lat"    : self._lat,
            "lon"    : self._lon,
            "alt"    : self._altitud,
            "vel_kmh": round(self.velocidad_kmh, 2),
            "rumbo"  : self._rumbo,
            "sats"   : self._num_sats,
            "fix"    : self._fix_quality,
            "valido" : self.esta_fijo(),
            "ts"     : int(time.time()),
        }

    def obtener_posicion_json(self):
        """
        Mismo contenido que obtener_posicion() pero serializado como string JSON.
        Listo para publicar en MQTT.
        """
        return json.dumps(self.obtener_posicion())


# =============================================================================
# CORUTINA STANDALONE: loop_gps
# Para usar en main.py junto con las demás corutinas de Safe-Path AI.
# =============================================================================

async def loop_gps(gps: GPSManager, mqtt=None, topico="safepath/gps",
                   intervalo_s=10, intervalo_sin_fix_s=30):
    """
    Corutina asyncio que mantiene el GPS actualizado y publica la posición
    periódicamente en MQTT.

    Parámetros:
        gps             : instancia de GPSManager
        mqtt            : instancia de MQTTManager (o None para no publicar)
        topico          : tópico MQTT donde publicar la posición
        intervalo_s     : segundos entre publicaciones con fix válido
        intervalo_sin_fix_s: segundos entre intentos cuando no hay fix

    Uso en main.py:
        asyncio.create_task(loop_gps(gps, mqtt, "safepath/gps"))
    """
    ultimo_envio = 0

    while True:
        # Leer UART continuamente (no bloqueante)
        gps.leer_uart()

        ahora = int(time.time())
        intervalo = intervalo_s if gps.esta_fijo() else intervalo_sin_fix_s

        if ahora - ultimo_envio >= intervalo:
            pos = gps.obtener_posicion()
            estado_txt = "fix" if pos["valido"] else "sin_fix"
            print(f"[GPS] {estado_txt} | lat={pos['lat']:.6f} lon={pos['lon']:.6f} "
                  f"sats={pos['sats']} vel={pos['vel_kmh']:.1f} km/h")

            if mqtt is not None:
                payload = json.dumps(pos)
                mqtt.publicar(topico, payload)

            ultimo_envio = ahora
            gc.collect()

        await asyncio.sleep(0.2)   # revisar UART cada 200 ms
