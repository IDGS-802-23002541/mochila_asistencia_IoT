# =============================================================================
# PROYECTO   : Vision Guard
# ARCHIVO    : main.py (Firmware Principal Corregido para ESP32)
# DESCRIPCIÓN: Controlador asíncrono que orquesta la lectura de telemetría,
#              la evaluación de riesgos y la publicación MQTT / Firebase.
# VERSIÓN    : 2.1 (Sin Cámara y con Lógica de Infrarrojos Laterales)
# =============================================================================

# ARCHIVOS NECESARIOS EN LA ESP32:
#   main.py          ← este archivo
#   dispositivos.py  ← HAL completa (E1)
#   hcsr04.py        ← driver ultrasonido (reciclado SmartCap)
#   imu.py           ← driver MPU6050    (reciclado SmartCap)
#   vector3d.py      ← soporte imu.py    (reciclado SmartCap)
#
# TÓPICOS MQTT:
#   Publica  → safepath/sensores   (JSON con resumen global cada 5 s)
#   Publica  → safepath/alertas    (string cuando detecta evento crítico)
#   Suscribe ← safepath/comandos   (comandos remotos: silencio, test, etc.)
#   Suscribe ← safepath/reconocido (nombre de persona detectada por YOLOv8)
# =============================================================================
import uasyncio as asyncio
import network
import json
import gc
from time import sleep, time
from machine import reset

from dispositivos import SensorBox, ActuatorBox, MQTTManager, FirebaseClient
from gps_manager  import GPSManager

# ─────────────────────────────────────────────────────────────────────────────
# CONFIGURACIÓN OPERATIVA (Ajustar por el equipo antes de flashear)
# ─────────────────────────────────────────────────────────────────────────────
REDES_WIFI = [
    ("INFINITUM8536_5", "4696601711"),
    ("CATA", "papantla"),
]

MQTT_BROKER    = "34.30.116.129"
MQTT_PUERTO    = 1883
MQTT_USUARIO   = "safepath_user"
MQTT_PASSWORD  = "SafePath2025!"
MQTT_CLIENT_ID = "safepath_mochila"

TOPICO_SENSORES   = "safepath/sensores"
TOPICO_ALERTAS    = "safepath/alertas"
TOPICO_COMANDOS   = "safepath/comandos"
TOPICO_RECONOCIDO = "safepath/reconocido"
TOPICO_GPS        = "safepath/gps"

FIREBASE_API_KEY   = "TU_API_KEY_AQUI"
FIREBASE_PROJECT   = "safe-path-ai"
FIREBASE_COLECCION = "safepath_events"

# Parámetros del GPS
GPS_UART_ID = 2
GPS_PIN_TX  = 17
GPS_PIN_RX  = 16
GPS_LAT_DEF = 21.1092
GPS_LON_DEF = -101.6275

# Umbrales lógicos del negocio
DISTANCIA_ALERTA_FRONTAL_CM = 100.0  # Alerta por debajo de 1 metro
INTERVALO_ALERTAS_VOZ_MS    = 3000   # Evita saturar el canal auditivo (3s)
INTERVALO_SENSORES_S        = 5      # Publicación MQTT
INTERVALO_FIREBASE_S        = 60     # Sincronización histórica nube
INTERVALO_GPS_S             = 10     # Muestreo GPS

# ─────────────────────────────────────────────────────────────────────────────
# ESTADO GLOBAL COMPARTIDO
# ─────────────────────────────────────────────────────────────────────────────
estado = {
    "wifi_ok"       : False,
    "mqtt_ok"       : False,
    "silenciado"    : False,
    "ultimo_resumen": {},
    "ultima_pos_gps": {},
}

# ─────────────────────────────────────────────────────────────────────────────
# CONEXIÓN WIFI
# ─────────────────────────────────────────────────────────────────────────────
async def conectar_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    for ssid, pwd in REDES_WIFI:
        print(f"[WiFi] Intentando conexión con: {ssid}")
        wlan.connect(ssid, pwd)
        for _ in range(15):
            if wlan.isconnected():
                print(f"[WiFi] Conectado exitosamente. IP: {wlan.ifconfig()[0]}")
                estado["wifi_ok"] = True
                return True
            await asyncio.sleep(1)
        wlan.disconnect()
        await asyncio.sleep(0.5)
    print("[WiFi] No se pudo establecer conexión con ninguna red.")
    return False

# ─────────────────────────────────────────────────────────────────────────────
# CALLBACKS MQTT
# ─────────────────────────────────────────────────────────────────────────────
def on_comando(topico, mensaje):
    print(f"[MQTT] Comando recibido: {mensaje}")
    if mensaje == "silencio":
        estado["silenciado"] = True
        actuadores.silenciar_todo()
    elif mensaje == "reanudar":
        estado["silenciado"] = False
        print("[MQTT] Modo activo reanudado.")
    elif mensaje == "test_buzzer":
        # En la versión física de Safe Path simulamos las alertas por bocina
        actuadores.reproducir_audio(ActuatorBox.PISTA_OBSTACULO_FRONTAL)

def on_reconocido(topico, mensaje):
    print(f"[MQTT] Persona identificada: {mensaje}")
    if estado["silenciado"]:
        return
    
    # Mapeo de pistas de identificación
    mapa = {
        "Desconocido": ActuatorBox.PISTA_DESCONOCIDO,
        "Persona1"   : 4,
        "Persona2"   : 5,
        "Persona3"   : 6,
    }
    actuadores.reproducir_audio(mapa.get(mensaje, ActuatorBox.PISTA_DESCONOCIDO))

# ─────────────────────────────────────────────────────────────────────────────
# CORUTINA 1 — Control de Sensores Locales e Inteligencia de Alertas
# ─────────────────────────────────────────────────────────────────────────────
async def loop_sensores():
    ultimo_tiempo_alerta = 0
    
    while True:
        if estado["silenciado"]:
            await asyncio.sleep(0.5)
            continue

        resumen = sensores.obtener_resumen_global()
        estado["ultimo_resumen"] = resumen

        dist = resumen.get("distancia_cm")
        ir_izq = resumen.get("ir_izq")
        ir_der = resumen.get("ir_der")
        caida = resumen.get("caida")

        # [BUZZER ACTIVO]: Se enciende inmediatamente a menos de 30 cm
        actuadores.actualizar_alerta_distancia(dist)

        # [MOTOR VIBRADOR]: Alerta háptica si hay un peligro inminente en cualquier flanco
        # Se activa por proximidad frontal media (<= 50 cm), sensores laterales o caídas.
        if (dist is not None and dist <= 50.0) or ir_izq or ir_der or caida:
            actuadores.activar_alerta_haptica()
        else:
            actuadores.desactivar_alerta_haptica()

        tiempo_actual = ticks_ms()

        # Evaluación de alertas prioritarias (una a la vez para no encimar audios)
        if ticks_diff(tiempo_actual, ultimo_tiempo_alerta) >= INTERVALO_ALERTAS_VOZ_MS:
            
            # Prioridad 1: Caídas críticas (MPU6050)
            if caida:
                actuadores.reproducir_audio(ActuatorBox.PISTA_CAIDA_DETECTADA)
                mqtt.publicar(TOPICO_ALERTAS, "ALERTA_CAIDA")
                ultimo_tiempo_alerta = ticks_ms()

            # Prioridad 2: Obstáculo Frontal de colisión directa (HC-SR04 <= 1 metro)
            elif dist is not None and dist <= DISTANCIA_ALERTA_FRONTAL_CM:
                actuadores.reproducir_audio(ActuatorBox.PISTA_OBSTACULO_FRONTAL)
                mqtt.publicar(TOPICO_ALERTAS, f"FRONTAL|dist={dist:.1f}")
                ultimo_tiempo_alerta = ticks_ms()

            # Prioridad 3: Obstáculo Lateral Izquierdo (IR Izquierdo)
            elif ir_izq:
                actuadores.reproducir_audio(ActuatorBox.PISTA_OBSTACULO_IZQ)
                mqtt.publicar(TOPICO_ALERTAS, "OBSTACULO_IZQUIERDA")
                ultimo_tiempo_alerta = ticks_ms()

            # Prioridad 4: Obstáculo Lateral Derecho (IR Derecho)
            elif ir_der:
                actuadores.reproducir_audio(ActuatorBox.PISTA_OBSTACULO_DER)
                mqtt.publicar(TOPICO_ALERTAS, "OBSTACULO_DERECHA")
                ultimo_tiempo_alerta = ticks_ms()
                

        await asyncio.sleep(0.2)  # Muestreo rápido para no perder lecturas cinemáticas

# ─────────────────────────────────────────────────────────────────────────────
# CORUTINA 2 — Publicación de Telemetría JSON (MQTT)
# ─────────────────────────────────────────────────────────────────────────────
async def loop_publicar_mqtt():
    while True:
        await asyncio.sleep(INTERVALO_SENSORES_S)
        if not estado["mqtt_ok"]:
            continue

        resumen = estado.get("ultimo_resumen", {})
        pos_gps = estado.get("ultima_pos_gps", {})
        
        if resumen:
            payload = json.dumps({
                "ts"    : int(time()),
                "dist"  : resumen.get("distancia_cm"),
                "ir_izq": resumen.get("ir_izq"),
                "ir_der": resumen.get("ir_der"),
                "caida" : resumen.get("caida"),
                "temp"  : resumen.get("temperatura"),
                "lat"   : pos_gps.get("lat"),
                "lon"   : pos_gps.get("lon"),
            })
            if mqtt.publicar(TOPICO_SENSORES, payload):
                print(f"[MQTT] Telemetría enviada: {payload}")

# ─────────────────────────────────────────────────────────────────────────────
# CORUTINA 3 — Escucha de Mensajes MQTT
# ─────────────────────────────────────────────────────────────────────────────
async def loop_mqtt_recv():
    while True:
        mqtt.verificar_mensajes()
        await asyncio.sleep(0.1)

# ─────────────────────────────────────────────────────────────────────────────
# CORUTINA 4 — Persistencia Histórica en Firebase Firestore
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
            "ir_izq"      : bool(resumen.get("ir_izq", False)),
            "ir_der"      : bool(resumen.get("ir_der", False)),
            "caida"       : bool(resumen.get("caida", False)),
            "temperatura" : float(resumen.get("temperatura") or 0.0),
            "lat"         : float(pos_gps.get("lat") or GPS_LAT_DEF),
            "lon"         : float(pos_gps.get("lon") or GPS_LON_DEF),
            "sats"        : int(pos_gps.get("sats") or 0),
        }
        
        ok = firebase.enviar_evento(datos)
        print(f"[Firebase] Sincronización histórica: {'ÉXITO' if ok else 'FALLO'}")
        gc.collect()

# ─────────────────────────────────────────────────────────────────────────────
# CORUTINA 5 — Navegación GPS (Ublox NEO-6M)
# ─────────────────────────────────────────────────────────────────────────────
async def loop_gps_wrapper():
    ultimo_envio = 0
    while True:
        if gps.leer_uart():
            estado["ultima_pos_gps"] = gps.obtener_posicion()
            
        ahora = int(time())
        intervalo = INTERVALO_GPS_S if gps.esta_fijo() else 30
        
        if ahora - ultimo_envio >= intervalo:
            pos = gps.obtener_posicion()
            estado["ultima_pos_gps"] = pos
            estado_txt = "CON_FIX" if pos["valido"] else "SIN_FIX"
            print(f"[GPS] {estado_txt} | Lat={pos['lat']:.6f} Lon={pos['lon']:.6f} | Sats={pos['sats']}")
            
            if estado["mqtt_ok"]:
                mqtt.publicar(TOPICO_GPS, gps.obtener_posicion_json())
            ultimo_envio = ahora
            
        await asyncio.sleep(0.2)

# ─────────────────────────────────────────────────────────────────────────────
# PUNTO DE INICIO (Orquestador Principal)
# ─────────────────────────────────────────────────────────────────────────────
async def main():
    global sensores, actuadores, mqtt, firebase, gps

    print("=" * 60)
    print("      SAFE-PATH AI — FIRMWARE DE CONTROL CENTRAL v2.1")
    print("      CONFIG: HC-SR04 | MPU6050 | 2x INFRARROJOS | GPS")
    print("=" * 60)

    # 1. Instanciación de Clases HAL
    sensores   = SensorBox()
    actuadores = ActuatorBox()
    gps        = GPSManager(uart_id=GPS_UART_ID,
                            pin_tx=GPS_PIN_TX,
                            pin_rx=GPS_PIN_RX,
                            lat_defecto=GPS_LAT_DEF,
                            lon_defecto=GPS_LON_DEF)

    # 2. Conectar Red local WiFi
    # wifi_ok = await conectar_wifi()

    # 3. Disparo asíncrono para obtención de señal GPS inicial
    # if wifi_ok:
    #     asyncio.create_task(gps.esperar_fix(timeout_s=30))

    # 4. Inicialización de Clientes IoT
    # mqtt = MQTTManager(broker=MQTT_BROKER, puerto=MQTT_PUERTO,
    #                    usuario=MQTT_USUARIO, contrasena=MQTT_PASSWORD,
    #                    client_id=MQTT_CLIENT_ID)
    # firebase = FirebaseClient(FIREBASE_API_KEY, FIREBASE_PROJECT,
    #                           FIREBASE_COLECCION)

    # # 5. Registro de Suscripciones MQTT
    # if wifi_ok:
    #     mqtt.registrar_callback(TOPICO_COMANDOS,   on_comando)
    #     mqtt.registrar_callback(TOPICO_RECONOCIDO, on_reconocido)
    #     estado["mqtt_ok"] = mqtt.conectar()

    # # 6. Lanzamiento del Pool de Corutinas en Paralelo
    # print("[Boot] Inicializando corutinas...")
    # asyncio.create_task(loop_sensores())
    # asyncio.create_task(loop_publicar_mqtt())
    # asyncio.create_task(loop_mqtt_recv())
    # asyncio.create_task(loop_firebase())
    # asyncio.create_task(loop_gps_wrapper())

    print("[Boot] Safe-Path arrancado exitosamente.\n")

    # Bucle infinito de soporte y reconexión activa
    # while True:
    #     if wifi_ok and not mqtt.conectado:
    #         print("[Soporte] Broker desconectado. Intentando reconexión activa...")
    #         estado["mqtt_ok"] = mqtt.conectar()
    #     await asyncio.sleep(10)


# Manejador de arranque seguro del procesador
try:
    asyncio.run(main())
except KeyboardInterrupt:
    print("\n[Sistema] Ejecución detenida de manera local.")
except Exception as e:
    print(f"\n[Sistema] Excepción crítica de sistema: {e} — Reiniciando procesador en 5 s...")
    sleep(5)
    reset()