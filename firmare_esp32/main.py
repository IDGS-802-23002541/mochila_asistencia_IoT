# =============================================================================
# PROYECTO   : Vision Guard — Sistema de Navegación Aumentada
# ARCHIVO    : main.py (Firmware Central de Control IoT de Producción)
# DESCRIPCIÓN: Controlador asíncrono que orquesta en paralelo la telemetría,
#              actualización de alertas físicas, geolocalización GPS,
#              comunicación por MQTT y sincronización periódica en Firebase.
# VERSIÓN    : 2.3 (Soporte de Infrarrojos, Alertas por Voz, Motor y Buzzer)
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
# CONFIGURACIÓN OPERATIVA (Ajustar credenciales de red local)
# ─────────────────────────────────────────────────────────────────────────────
REDES_WIFI = [
    ("INFINITUM8536_5", "4696601711"), # <-- Agrega la red de tu casa/escuela
    ("CATA", "papantla"),    # Red del campus
]

# Broker MQTT central de Diego
MQTT_BROKER    = "34.30.116.129"
MQTT_PUERTO    = 8883
MQTT_USUARIO   = "diegosa9_"
MQTT_PASSWORD  = "Diegosa9"
MQTT_CLIENT_ID = "vision_guard"

# Canales de comunicación MQTT
TOPICO_SENSORES   = "safepath/sensores"
TOPICO_ALERTAS    = "safepath/alertas"
TOPICO_COMANDOS   = "safepath/comandos"
TOPICO_GPS        = "safepath/gps"

# Parámetros de la Base de Datos Firebase Firestore (Sincronización histórica)
FIREBASE_API_KEY   = "TU_API_KEY_AQUI"
FIREBASE_PROJECT   = "safe-path-ai"
FIREBASE_COLECCION = "safepath_events"

# Configuración del Puerto Serial de Hardware (UART2) - ¡VALIDADO A 115200 BPS!
GPS_UART_ID = 2
GPS_PIN_TX  = 17
GPS_PIN_RX  = 16
GPS_LAT_DEF = 21.155614  # <-- Actualizado a tus coordenadas reales obtenidas
GPS_LON_DEF = -101.680390 # <-- Actualizado a tus coordenadas reales obtenidas

# Tiempos de ciclo y umbrales operacionales
DISTANCIA_ALERTA_FRONTAL_CM = 100.0  # Alerta de voz por debajo de 1 metro
INTERVALO_ALERTAS_VOZ_MS    = 3000   # Bloqueo de audio de 3 segundos para la bocina
INTERVALO_SENSORES_S        = 5      # Envío de telemetría por MQTT
INTERVALO_FIREBASE_S        = 60     # Sincronización analítica nube
INTERVALO_GPS_S             = 10     # Muestreo de posición satelital

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
# CONEXIÓN A LA RED WIFI
# ─────────────────────────────────────────────────────────────────────────────
async def conectar_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    for ssid, pwd in REDES_WIFI:
        print(f"[WiFi] Buscando red: {ssid}")
        wlan.connect(ssid, pwd)
        for _ in range(15):
            if wlan.isconnected():
                print(f"[WiFi] Conectado. IP Asignada: {wlan.ifconfig()[0]}")
                estado["wifi_ok"] = True
                return True
            await asyncio.sleep(1)
        wlan.disconnect()
        await asyncio.sleep(0.5)
    print("[WiFi] Sin conexión WiFi. Operando de forma local (Offline-Ready).")
    return False

# ─────────────────────────────────────────────────────────────────────────────
# PROCESAMIENTO DE COMANDOS REMOTOS (Suscripciones MQTT)
# ─────────────────────────────────────────────────────────────────────────────
def on_comando(topico, mensaje):
    print(f"[MQTT] Comando recibido desde servidor: {mensaje}")
    if mensaje == "silencio":
        estado["silenciado"] = True
        actuadores.silenciar_todo()
    elif mensaje == "reanudar":
        estado["silenciado"] = False
        print("[MQTT] Modo activo reanudado con éxito.")
    elif mensaje == "test_alertas":
        # Comando remoto para verificar buzzer y vibrador
        actuadores.activar_alerta_haptica()
        actuadores.encender_buzzer()
        sleep(0.5)
        actuadores.silenciar_todo()

# ─────────────────────────────────────────────────────────────────────────────
# CORUTINA 1 — Control de Hardware, Alertas Físicas e Inteligencia de Tropiezos
# ─────────────────────────────────────────────────────────────────────────────
async def loop_sensores():
    ultimo_tiempo_alerta_voz = 0
    from utime import ticks_ms, ticks_diff
    
    while True:
        if estado["silenciado"]:
            await asyncio.sleep(0.5)
            continue

        # 1. Adquisición síncrona de telemetría a través de la HAL
        resumen = sensores.obtener_resumen_global()
        estado["ultimo_resumen"] = resumen

        dist = resumen.get("distancia_cm")
        ir_izq = resumen.get("ir_izq")
        ir_der = resumen.get("ir_der")
        caida = resumen.get("caida") # 'caida' representa tropiezos calibrados a 1.5G

        # 2. ACTUALIZACIÓN AUTOMÁTICA DEL BUZZER SEGÚN LA DISTANCIA
        # Si la distancia es <= 30cm, el buzzer activo se encenderá físicamente.
        actuadores.actualizar_alerta_distancia(dist)

        # 3. Lógica para el motor de vibración (Alerta Háptica de Proximidad)
        # Se activa si hay un obstáculo frontal a menos de 50 cm, laterales, o un tropiezo
        if (dist is not None and dist <= 50.0) or ir_izq or ir_der or caida:
            actuadores.activar_alerta_haptica()
        else:
            actuadores.desactivar_alerta_haptica()

        # 4. Evaluación de Mensajes de Guía por Voz (DFPlayer Mini)
        # Se prioriza una alerta a la vez para evitar sonidos sobrepuestos en la bocina
        tiempo_actual = ticks_ms()
        if ticks_diff(tiempo_actual, ultimo_tiempo_alerta_voz) >= INTERVALO_ALERTAS_VOZ_MS:
            
            # Prioridad 1: Tropiezo detectado (Aceleración MPU6050 > 1.5G)
            if caida:
                actuadores.reproducir_audio(ActuatorBox.PISTA_CAIDA_DETECTADA)
                mqtt.publicar(TOPICO_ALERTAS, "ALERTA_TROPIEZO")
                ultimo_tiempo_alerta_voz = tiempo_actual

            # Prioridad 2: Obstáculo frontal detectado (Ultrasónico <= 1 metro)
            elif dist is not None and dist <= DISTANCIA_ALERTA_FRONTAL_CM:
                actuadores.reproducir_audio(ActuatorBox.PISTA_OBSTACULO_FRONTAL)
                mqtt.publicar(TOPICO_ALERTAS, f"FRONTAL|dist={dist:.1f}")
                ultimo_tiempo_alerta_voz = tiempo_actual

            # Prioridad 3: Obstáculo cercano por la izquierda (FC-51 Izquierdo)
            elif ir_izq:
                actuadores.reproducir_audio(ActuatorBox.PISTA_OBSTACULO_IZQ)
                mqtt.publicar(TOPICO_ALERTAS, "OBSTACULO_IZQUIERDA")
                ultimo_tiempo_alerta_voz = tiempo_actual

            # Prioridad 4: Obstáculo cercano por la derecha (FC-51 Derecho)
            elif ir_der:
                actuadores.reproducir_audio(ActuatorBox.PISTA_OBSTACULO_DER)
                mqtt.publicar(TOPICO_ALERTAS, "OBSTACULO_DERECHA")
                ultimo_tiempo_alerta_voz = tiempo_actual

        await asyncio.sleep(0.2)  # Muestreo rápido no bloqueante (200 ms)

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
# CORUTINA 3 — Escucha Activa de Mensajes MQTT
# ─────────────────────────────────────────────────────────────────────────────
async def loop_mqtt_recv():
    while True:
        mqtt.verificar_mensajes()
        await asyncio.sleep(0.1)

# ─────────────────────────────────────────────────────────────────────────────
# CORUTINA 4 — Sincronización de Datos Históricos en la Nube (Firebase)
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

        # Estructura de datos analítica compatible con el Data Warehouse
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
        print(f"[Firebase] Sincronización histórica: {'EXITOSA' if ok else 'FALLIDA'}")
        gc.collect()

# ─────────────────────────────────────────────────────────────────────────────
# CORUTINA 5 — Geolocalización Activa (NEO-6M a 115200 bps)
# ─────────────────────────────────────────────────────────────────────────────
async def loop_gps_wrapper():
    ultimo_envio = 0
    while True:
        # Lectura serial asíncrona continua por UART2
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
# ORQUESTRADOR PRINCIPAL (Arranque del Sistema)
# ─────────────────────────────────────────────────────────────────────────────
async def main():
    global sensores, actuadores, mqtt, firebase, gps

    print("=" * 60)
    print("      VISION GUARD — FIRMWARE DE CONTROL CENTRAL v2.3")
    print("      CONFIG: HC-SR04 | MPU6050 | 2x INFRARROJOS | MOTOR | BUZZER")
    print("=" * 60)

    # 1. Instanciación de componentes mediante la HAL (Seguridad de Pines)
    sensores   = SensorBox(umbral_caida=1.5) # <-- Calibrado de tropiezo a 1.5G
    actuadores = ActuatorBox()
    
    # 2. Inicialización del GPS con velocidad validada a 115200 bps
    gps        = GPSManager(uart_id=GPS_UART_ID,
                            pin_tx=GPS_PIN_TX,
                            pin_rx=GPS_PIN_RX,
                            baudrate=115200,
                            lat_defecto=GPS_LAT_DEF,
                            lon_defecto=GPS_LON_DEF)

    # 3. Conectar Red WiFi local
    wifi_ok = await conectar_wifi()

    # 4. Disparar temporizador asíncrono para obtención de señal GPS inicial
    if wifi_ok:
        asyncio.create_task(gps.esperar_fix(timeout_s=30))

    # 5. Inicializar clientes de Nube (Diego)
    mqtt = MQTTManager(broker=MQTT_BROKER, puerto=MQTT_PUERTO,
                       usuario=MQTT_USUARIO, contrasena=MQTT_PASSWORD,
                       client_id=MQTT_CLIENT_ID)
    firebase = FirebaseClient(FIREBASE_API_KEY, FIREBASE_PROJECT,
                              FIREBASE_COLECCION)

    # 6. Configurar callbacks de comandos e iniciar Broker
    if wifi_ok:
        mqtt.registrar_callback(TOPICO_COMANDOS, on_comando)
        estado["mqtt_ok"] = mqtt.conectar()

    # 7. Ejecución del pool de tareas en paralelo
    print("[Boot] Iniciando sistema de tareas asíncronas...")
    asyncio.create_task(loop_sensores())
    asyncio.create_task(loop_publicar_mqtt())
    asyncio.create_task(loop_mqtt_recv())
    asyncio.create_task(loop_firebase())
    asyncio.create_task(loop_gps_wrapper())

    print("[Boot] Safe-Path funcionando al 100%.\n")

    # Bucle infinito para monitoreo de estado y reconexión activa de MQTT
    while True:
        if wifi_ok and not mqtt.conectado:
            print("[Soporte] Broker desconectado. Intentando reconexión activa...")
            estado["mqtt_ok"] = mqtt.conectar()
        await asyncio.sleep(10)


# Manejador de arranque seguro del hardware
try:
    asyncio.run(main())
except KeyboardInterrupt:
    print("\n[Sistema] Ejecución detenida de manera local.")
except Exception as e:
    print(f"\n[Sistema] Excepción crítica de sistema: {e} — Reiniciando procesador en 5 s...")
    sleep(5)
    reset()