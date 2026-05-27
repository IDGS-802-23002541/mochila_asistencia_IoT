# =============================================================================
# PROYECTO   : Safe-Path AI — Sistema de Navegación Aumentada
# ARCHIVO    : main.py  (Firmware completo — E2)
# DESCRIPCIÓN: Firmware principal con 6 corutinas asyncio:
#                1. loop_sensores()      — HC-SR04, LDR, MPU6050 cada 200 ms
#                2. loop_publicar_mqtt() — telemetría JSON cada 5 s
#                3. loop_mqtt_recv()     — mensajes entrantes cada 100 ms
#                4. loop_firebase()      — escritura Firestore cada 60 s
#                5. loop_gps_wrapper()  — GPS Ublox NEO-6M cada 10 s
#                6. loop_camera()       — frame ESP32-CAM al servidor IA
# INTEGRANTES: [Nombres del equipo Safe-Path AI]
# VERSIÓN    : 2.0  (GPS + Cámara integrados)
# =============================================================================

import uasyncio as asyncio
import network
import json
import gc
from time import sleep, time
from machine import reset

# Intento de importar cámara (solo disponible en ESP32-CAM)
try:
    import urequests
    import camera
    CAMERA_DISPONIBLE = True
except ImportError:
    CAMERA_DISPONIBLE = False

from dispositivos import SensorBox, ActuatorBox, MQTTManager, FirebaseClient
from gps_manager  import GPSManager

# ─────────────────────────────────────────────────────────────────────────────
# CONFIGURACIÓN — editar antes de flashear
# ─────────────────────────────────────────────────────────────────────────────
REDES_WIFI = [
    ("NombreRed1",  "contrasena1"),
    ("NombreRed2",  "contrasena2"),
    ("Alumnos-TecNM-D-UF", ""),
]

MQTT_BROKER    = "34.30.116.129"
MQTT_PUERTO    = 1883
MQTT_USUARIO   = "safepath_user"
MQTT_PASSWORD  = "SafePath2025!"
MQTT_CLIENT_ID = "safepath_mochila"

TOPICO_SENSORES    = "safepath/sensores"
TOPICO_ALERTAS     = "safepath/alertas"
TOPICO_COMANDOS    = "safepath/comandos"
TOPICO_RECONOCIDO  = "safepath/reconocido"
TOPICO_GPS         = "safepath/gps"

FIREBASE_API_KEY   = "TU_API_KEY_AQUI"
FIREBASE_PROJECT   = "safe-path-ai"
FIREBASE_COLECCION = "safepath_events"

GPS_UART_ID  = 2
GPS_PIN_TX   = 17
GPS_PIN_RX   = 16
GPS_LAT_DEF  = 21.1092
GPS_LON_DEF  = -101.6275

SERVIDOR_URL         = "http://TU_IP_SERVIDOR:8080"
URL_UPLOAD_FRAME     = SERVIDOR_URL + "/upload_frame_mochila"
INTERVALO_FRAME_S    = 10

DISTANCIA_ALERTA_CM  = 80.0
DISTANCIA_CRITICA_CM = 30.0
INTERVALO_SENSORES_S = 5
INTERVALO_FIREBASE_S = 60
INTERVALO_GPS_S      = 10

# ─────────────────────────────────────────────────────────────────────────────
# ESTADO GLOBAL
# ─────────────────────────────────────────────────────────────────────────────
estado = {
    "wifi_ok"       : False,
    "mqtt_ok"       : False,
    "silenciado"    : False,
    "ultimo_resumen": {},
    "ultima_pos_gps": {},
}

# ─────────────────────────────────────────────────────────────────────────────
# WIFI
# ─────────────────────────────────────────────────────────────────────────────
async def conectar_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    for ssid, pwd in REDES_WIFI:
        print(f"[WiFi] Intentando: {ssid}")
        wlan.connect(ssid, pwd)
        for _ in range(15):
            if wlan.isconnected():
                print(f"[WiFi] Conectado: {wlan.ifconfig()}")
                estado["wifi_ok"] = True
                return True
            await asyncio.sleep(1)
        wlan.disconnect()
        await asyncio.sleep(0.5)
    print("[WiFi] Sin conexión.")
    return False

# ─────────────────────────────────────────────────────────────────────────────
# CÁMARA  (reciclado de final.py del carrito)
# ─────────────────────────────────────────────────────────────────────────────
def _init_camera():
    try:
        camera.init(0, format=camera.JPEG)
        print("[Camera] Inicializada.")
        return True
    except Exception as e:
        print(f"[Camera] Error: {e}")
        return False


async def loop_camera():
    if not CAMERA_DISPONIBLE or not _init_camera():
        print("[Camera] Corutina desactivada.")
        return
    while True:
        await asyncio.sleep(INTERVALO_FRAME_S)
        if not estado["wifi_ok"]:
            continue
        try:
            frame = camera.capture()
            if frame:
                resp = urequests.post(URL_UPLOAD_FRAME,
                                      data=frame,
                                      headers={"Content-Type": "image/jpeg"})
                resp.close()
                gc.collect()
        except Exception as e:
            print(f"[Camera] Error al enviar: {e}")
            gc.collect()

# ─────────────────────────────────────────────────────────────────────────────
# CALLBACKS MQTT
# ─────────────────────────────────────────────────────────────────────────────
def on_comando(topico, mensaje):
    print(f"[MQTT] Comando: {mensaje}")
    if mensaje == "silencio":
        estado["silenciado"] = True
        actuadores.silenciar_todo()
    elif mensaje == "reanudar":
        estado["silenciado"] = False
    elif mensaje == "test_buzzer":
        actuadores.alerta_critica(pulsos=1, duracion_ms=150, cooldown_ms=0)
    elif mensaje == "test_vibra":
        actuadores.activar_vibracion(duracion_ms=300, cooldown_ms=0)


def on_reconocido(topico, mensaje):
    print(f"[MQTT] Persona: {mensaje}")
    if estado["silenciado"]:
        return
    mapa = {
        "Desconocido": ActuatorBox.PISTA_DESCONOCIDO,
        "Persona1"   : 4,
        "Persona2"   : 5,
        "Persona3"   : 6,
    }
    actuadores.reproducir_audio(mapa.get(mensaje, ActuatorBox.PISTA_DESCONOCIDO))

# ─────────────────────────────────────────────────────────────────────────────
# CORUTINA 1 — Sensores locales
# ─────────────────────────────────────────────────────────────────────────────
async def loop_sensores():
    while True:
        if estado["silenciado"]:
            await asyncio.sleep(0.5)
            continue
        resumen = sensores.obtener_resumen_global()
        estado["ultimo_resumen"] = resumen
        dist = resumen.get("distancia_cm")
        if dist is not None:
            if dist <= DISTANCIA_CRITICA_CM:
                actuadores.alerta_critica(pulsos=3, duracion_ms=200)
                actuadores.activar_vibracion(duracion_ms=400)
                actuadores.reproducir_audio(ActuatorBox.PISTA_OBSTACULO_CERCA)
                mqtt.publicar(TOPICO_ALERTAS, f"critico|dist={dist:.1f}")
            elif dist <= DISTANCIA_ALERTA_CM:
                actuadores.activar_vibracion(duracion_ms=200, cooldown_ms=600)
                mqtt.publicar(TOPICO_ALERTAS, f"proximo|dist={dist:.1f}")
        if resumen.get("caida"):
            actuadores.alerta_critica(pulsos=5, duracion_ms=100, cooldown_ms=3000)
            actuadores.reproducir_audio(ActuatorBox.PISTA_CAIDA_DETECTADA)
            mqtt.publicar(TOPICO_ALERTAS, "caida_detectada")
        if resumen.get("oscuro"):
            actuadores.reproducir_audio(ActuatorBox.PISTA_LUZ_BAJA)
        await asyncio.sleep(0.2)

# ─────────────────────────────────────────────────────────────────────────────
# CORUTINA 2 — Telemetría MQTT
# ─────────────────────────────────────────────────────────────────────────────
async def loop_publicar_mqtt():
    while True:
        await asyncio.sleep(INTERVALO_SENSORES_S)
        if not estado["mqtt_ok"]:
            continue
        resumen = estado.get("ultimo_resumen", {})
        pos_gps = estado.get("ultima_pos_gps", {})
        if not resumen:
            continue
        payload = json.dumps({
            "ts"    : int(time()),
            "dist"  : resumen.get("distancia_cm"),
            "oscuro": resumen.get("oscuro"),
            "caida" : resumen.get("caida"),
            "temp"  : resumen.get("temperatura"),
            "lat"   : pos_gps.get("lat"),
            "lon"   : pos_gps.get("lon"),
        })
        if mqtt.publicar(TOPICO_SENSORES, payload):
            print(f"[MQTT] Telemetría: {payload}")

# ─────────────────────────────────────────────────────────────────────────────
# CORUTINA 3 — Recepción MQTT
# ─────────────────────────────────────────────────────────────────────────────
async def loop_mqtt_recv():
    while True:
        mqtt.verificar_mensajes()
        await asyncio.sleep(0.1)

# ─────────────────────────────────────────────────────────────────────────────
# CORUTINA 4 — Firebase Firestore
# ─────────────────────────────────────────────────────────────────────────────
async def loop_firebase():
    while True:
        await asyncio.sleep(INTERVALO_FIREBASE_S)
        if not estado["wifi_ok"]:
            continue
        resumen = estado.get("ultimo_resumen", {})
        pos_gps = estado.get("ultima_pos_gps", {})
        if not resumen:
            continue
        datos = {
            "timestamp"   : int(time()),
            "tipo"        : "telemetria",
            "distancia_cm": float(resumen.get("distancia_cm") or -1),
            "oscuro"      : bool(resumen.get("oscuro", False)),
            "caida"       : bool(resumen.get("caida", False)),
            "temperatura" : float(resumen.get("temperatura") or 0),
            "lat"         : float(pos_gps.get("lat") or GPS_LAT_DEF),
            "lon"         : float(pos_gps.get("lon") or GPS_LON_DEF),
            "sats"        : int(pos_gps.get("sats") or 0),
        }
        ok = firebase.enviar_evento(datos)
        print(f"[Firebase] {'OK' if ok else 'FALLO'}")
        gc.collect()

# ─────────────────────────────────────────────────────────────────────────────
# CORUTINA 5 — GPS Ublox NEO-6M
# ─────────────────────────────────────────────────────────────────────────────
async def loop_gps_wrapper():
    ultimo_envio = 0
    while True:
        if gps.leer_uart():
            estado["ultima_pos_gps"] = gps.obtener_posicion()
        ahora   = int(time())
        intervalo = INTERVALO_GPS_S if gps.esta_fijo() else 30
        if ahora - ultimo_envio >= intervalo:
            pos = gps.obtener_posicion()
            estado["ultima_pos_gps"] = pos
            estado_txt = "FIX" if pos["valido"] else "SIN_FIX"
            print(f"[GPS] {estado_txt} | lat={pos['lat']:.6f} "
                  f"lon={pos['lon']:.6f} | sats={pos['sats']} "
                  f"vel={pos['vel_kmh']:.1f} km/h | alt={pos['alt']} m")
            if estado["mqtt_ok"]:
                mqtt.publicar(TOPICO_GPS, gps.obtener_posicion_json())
            ultimo_envio = ahora
        await asyncio.sleep(0.2)

# ─────────────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────────────
async def main():
    global sensores, actuadores, mqtt, firebase, gps

    print("=" * 50)
    print("  Safe-Path AI — Firmware v2.0")
    print("  HC-SR04 | LDR | MPU6050 | GPS | CAM")
    print("=" * 50)

    # 1. Hardware
    sensores   = SensorBox()
    actuadores = ActuatorBox()
    gps        = GPSManager(uart_id=GPS_UART_ID,
                            pin_tx=GPS_PIN_TX,
                            pin_rx=GPS_PIN_RX,
                            lat_defecto=GPS_LAT_DEF,
                            lon_defecto=GPS_LON_DEF)

    # 2. WiFi
    wifi_ok = await conectar_wifi()

    # 3. Esperar fix GPS inicial (30 s máx) si hay WiFi
    if wifi_ok:
        asyncio.create_task(gps.esperar_fix(timeout_s=30))

    # 4. Clientes de nube
    mqtt = MQTTManager(broker=MQTT_BROKER, puerto=MQTT_PUERTO,
                       usuario=MQTT_USUARIO, contrasena=MQTT_PASSWORD,
                       client_id=MQTT_CLIENT_ID)
    firebase = FirebaseClient(FIREBASE_API_KEY, FIREBASE_PROJECT,
                              FIREBASE_COLECCION)

    # 5. Conectar MQTT
    if wifi_ok:
        mqtt.registrar_callback(TOPICO_COMANDOS,   on_comando)
        mqtt.registrar_callback(TOPICO_RECONOCIDO, on_reconocido)
        estado["mqtt_ok"] = mqtt.conectar()

    # 6. Lanzar 6 corutinas en paralelo
    print("[Boot] Lanzando corutinas...")
    asyncio.create_task(loop_sensores())
    asyncio.create_task(loop_publicar_mqtt())
    asyncio.create_task(loop_mqtt_recv())
    asyncio.create_task(loop_firebase())
    asyncio.create_task(loop_gps_wrapper())
    asyncio.create_task(loop_camera())

    print("[Boot] Sistema activo.\n")

    # Loop de mantenimiento: reconexión MQTT automática
    while True:
        if wifi_ok and not mqtt.conectado:
            print("[Maint] Reconectando MQTT...")
            estado["mqtt_ok"] = mqtt.conectar()
        await asyncio.sleep(10)


try:
    asyncio.run(main())
except KeyboardInterrupt:
    print("\n[Sistema] Detenido.")
except Exception as e:
    print(f"\n[Sistema] Error: {e} — reiniciando en 5 s...")
    sleep(5)
    reset()
