# =============================================================================
# PROYECTO   : Safe-Path AI — Sistema de Navegación Aumentada
# ARCHIVO    : main.py   (Entregable E2 — Integración MQTT)
# DESCRIPCIÓN: Firmware principal que integra la HAL (dispositivos.py) con
#              comunicación MQTT bidireccional y envío periódico a Firebase.
#              Arquitectura no bloqueante con uasyncio (igual que SmartCap).
# INTEGRANTES: [Nombres del equipo Safe-Path AI]
# VERSIÓN    : 1.0
# =============================================================================
#
# ARCHIVOS NECESARIOS EN LA ESP32 / ESP32-CAM:
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
from utime import ticks_ms, ticks_diff
from machine import reset

from dispositivos import SensorBox, ActuatorBox, MQTTManager, FirebaseClient

# ─────────────────────────────────────────────────────────────────────────────
# CONFIGURACIÓN — editar por el equipo antes de flashear
# ─────────────────────────────────────────────────────────────────────────────
REDES_WIFI = [
    ("NombreRed1",  "contrasena1"),
    ("NombreRed2",  "contrasena2"),
    ("Alumnos-TecNM-D-UF", ""),
]

MQTT_BROKER    = "34.30.116.129"   # IP del broker (reusar el de SmartCap)
MQTT_PUERTO    = 1883
MQTT_USUARIO   = "safepath_user"
MQTT_PASSWORD  = "SafePath2025!"
MQTT_CLIENT_ID = "safepath_mochila"

TOPICO_SENSORES    = "safepath/sensores"
TOPICO_ALERTAS     = "safepath/alertas"
TOPICO_COMANDOS    = "safepath/comandos"
TOPICO_RECONOCIDO  = "safepath/reconocido"

FIREBASE_API_KEY   = "TU_API_KEY_AQUI"
FIREBASE_PROJECT   = "safe-path-ai"
FIREBASE_COLECCION = "eventos"

# Umbrales de alerta (configurables sin tocar la HAL)
DISTANCIA_ALERTA_CM    = 80.0   # cm — activa buzzer y vibración
DISTANCIA_CRITICA_CM   = 30.0   # cm — activa alerta crítica (buzzer 3 pulsos)
INTERVALO_SENSORES_S   = 5      # segundos entre publicaciones MQTT de telemetría
INTERVALO_FIREBASE_S   = 60     # segundos entre escrituras a Firestore

# ─────────────────────────────────────────────────────────────────────────────
# Estado global compartido entre corutinas
# ─────────────────────────────────────────────────────────────────────────────
estado = {
    "wifi_ok"     : False,
    "mqtt_ok"     : False,
    "silenciado"  : False,    # modo silencio activado por comando remoto
    "ultimo_resumen": {},
}


# ─────────────────────────────────────────────────────────────────────────────
# WIFI
# ─────────────────────────────────────────────────────────────────────────────
async def conectar_wifi():
    """
    Intenta conectar a cada red de REDES_WIFI hasta lograrlo.
    Devuelve True si conectó, False si agotó todas las opciones.
    """
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)

    for ssid, pwd in REDES_WIFI:
        print(f"[WiFi] Intentando: {ssid}")
        wlan.connect(ssid, pwd)
        for _ in range(10):
            if wlan.isconnected():
                print(f"[WiFi] Conectado: {wlan.ifconfig()}")
                estado["wifi_ok"] = True
                return True
            await asyncio.sleep(1)
        wlan.disconnect()
        await asyncio.sleep(0.5)

    print("[WiFi] No se pudo conectar a ninguna red.")
    return False


# ─────────────────────────────────────────────────────────────────────────────
# CALLBACKS MQTT — qué hace el sistema cuando llega un mensaje
# ─────────────────────────────────────────────────────────────────────────────
def on_comando(topico, mensaje):
    """
    Maneja comandos remotos desde la interfaz web o dashboard.
    Comandos reconocidos:
        silencio     → desactiva todos los actuadores
        reanudar     → vuelve al modo activo
        test_buzzer  → prueba el buzzer (1 pitido)
        test_vibra   → prueba el motor vibrador (1 pulso)
    """
    print(f"[MQTT] Comando recibido: {mensaje}")
    if mensaje == "silencio":
        estado["silenciado"] = True
        actuadores.silenciar_todo()
    elif mensaje == "reanudar":
        estado["silenciado"] = False
        print("[Comandos] Modo activo reanudado.")
    elif mensaje == "test_buzzer":
        actuadores.alerta_critica(pulsos=1, duracion_ms=150, cooldown_ms=0)
    elif mensaje == "test_vibra":
        actuadores.activar_vibracion(duracion_ms=300, cooldown_ms=0)
    else:
        print(f"[Comandos] Comando desconocido: '{mensaje}'")


def on_reconocido(topico, mensaje):
    """
    Recibe el nombre de la persona detectada por YOLOv8 en el servidor IA.
    Reproduce el audio correspondiente vía DFPlayer.
    (Misma lógica que audio_personas() en SmartCapFinal.py)
    """
    print(f"[MQTT] Persona reconocida: {mensaje}")
    if estado["silenciado"]:
        return

    # Mapa de personas → pista de audio (numeradas en la SD del DFPlayer)
    mapa_personas = {
        "Desconocido"    : ActuatorBox.PISTA_DESCONOCIDO,
        "Persona1"       : 4,
        "Persona2"       : 5,
        "Persona3"       : 6,
    }
    pista = mapa_personas.get(mensaje, ActuatorBox.PISTA_DESCONOCIDO)
    actuadores.reproducir_audio(pista)


# ─────────────────────────────────────────────────────────────────────────────
# CORUTINA 1: Lectura de sensores y lógica de alertas locales
# ─────────────────────────────────────────────────────────────────────────────
async def loop_sensores():
    """
    Lee los sensores cada 200 ms, evalúa umbrales y activa actuadores.
    No bloquea gracias a asyncio — reciclado del patrón de SmartCap.
    """
    while True:
        if estado["silenciado"]:
            await asyncio.sleep(0.5)
            continue

        resumen = sensores.obtener_resumen_global()
        estado["ultimo_resumen"] = resumen

        dist = resumen.get("distancia_cm")

        # ── Alerta de proximidad ─────────────────────────────────────────────
        if dist is not None:
            if dist <= DISTANCIA_CRITICA_CM:
                # Colisión inminente: 3 pitidos + vibración
                actuadores.alerta_critica(pulsos=3, duracion_ms=200)
                actuadores.activar_vibracion(duracion_ms=400)
                mqtt.publicar(TOPICO_ALERTAS, f"critico|dist={dist:.1f}")

            elif dist <= DISTANCIA_ALERTA_CM:
                # Objeto cercano: 1 pitido + vibración
                actuadores.activar_vibracion(duracion_ms=200, cooldown_ms=600)
                mqtt.publicar(TOPICO_ALERTAS, f"proximo|dist={dist:.1f}")

        # ── Alerta de caída ──────────────────────────────────────────────────
        if resumen.get("caida"):
            actuadores.alerta_critica(pulsos=5, duracion_ms=100, cooldown_ms=3000)
            actuadores.reproducir_audio(ActuatorBox.PISTA_CAIDA_DETECTADA)
            mqtt.publicar(TOPICO_ALERTAS, "caida_detectada")

        # ── Alerta de oscuridad ──────────────────────────────────────────────
        if resumen.get("oscuro"):
            actuadores.reproducir_audio(ActuatorBox.PISTA_LUZ_BAJA)

        await asyncio.sleep(0.2)


# ─────────────────────────────────────────────────────────────────────────────
# CORUTINA 2: Publicación periódica de telemetría MQTT
# ─────────────────────────────────────────────────────────────────────────────
async def loop_publicar_mqtt():
    """
    Publica el resumen de sensores en JSON cada INTERVALO_SENSORES_S segundos.
    Tópico: safepath/sensores
    """
    while True:
        await asyncio.sleep(INTERVALO_SENSORES_S)

        if not estado["mqtt_ok"]:
            continue

        resumen = estado.get("ultimo_resumen", {})
        if resumen:
            payload = json.dumps({
                "ts"     : int(time()),
                "dist"   : resumen.get("distancia_cm"),
                "oscuro" : resumen.get("oscuro"),
                "caida"  : resumen.get("caida"),
                "temp"   : resumen.get("temperatura"),
            })
            ok = mqtt.publicar(TOPICO_SENSORES, payload)
            if ok:
                print(f"[MQTT] Telemetría publicada: {payload}")


# ─────────────────────────────────────────────────────────────────────────────
# CORUTINA 3: Verificación de mensajes MQTT entrantes
# ─────────────────────────────────────────────────────────────────────────────
async def loop_mqtt_recv():
    """
    Llama a check_msg() cada 100 ms para no perder mensajes entrantes.
    Patrón reciclado de listen_mqtt() en SmartCapFinal.py.
    """
    while True:
        mqtt.verificar_mensajes()
        await asyncio.sleep(0.1)


# ─────────────────────────────────────────────────────────────────────────────
# CORUTINA 4: Envío periódico de eventos a Firebase
# ─────────────────────────────────────────────────────────────────────────────
async def loop_firebase():
    """
    Envía el resumen de sensores a Firestore cada INTERVALO_FIREBASE_S segundos.
    Patrón reciclado de subir_datos_periodicamente() en SmartCapFinal.py.
    """
    while True:
        await asyncio.sleep(INTERVALO_FIREBASE_S)

        if not estado["wifi_ok"]:
            continue

        resumen = estado.get("ultimo_resumen", {})
        if not resumen:
            continue

        datos = {
            "timestamp"   : int(time()),
            "distancia_cm": resumen.get("distancia_cm", -1.0) or -1.0,
            "oscuro"      : resumen.get("oscuro", False),
            "caida"       : resumen.get("caida", False),
            "temperatura" : resumen.get("temperatura", 0.0),
        }
        ok = firebase.enviar_evento(datos)
        print(f"[Firebase] Evento enviado: {'OK' if ok else 'FALLO'}")
        gc.collect()


# ─────────────────────────────────────────────────────────────────────────────
# MAIN: inicialización y arranque de todas las corutinas
# ─────────────────────────────────────────────────────────────────────────────
async def main():
    global sensores, actuadores, mqtt, firebase

    print("=" * 50)
    print("  Safe-Path AI — Firmware v1.0")
    print("=" * 50)

    # 1. Instanciar HAL (ningún Pin en este scope)
    print("[Boot] Inicializando hardware...")
    sensores   = SensorBox()
    actuadores = ActuatorBox()

    # 2. Conectar WiFi
    wifi_ok = await conectar_wifi()
    if not wifi_ok:
        print("[Boot] Sin WiFi — operando en modo local (sin MQTT/Firebase).")

    # 3. Inicializar clientes de nube
    mqtt = MQTTManager(
        broker    = MQTT_BROKER,
        puerto    = MQTT_PUERTO,
        usuario   = MQTT_USUARIO,
        contrasena= MQTT_PASSWORD,
        client_id = MQTT_CLIENT_ID,
    )
    firebase = FirebaseClient(FIREBASE_API_KEY, FIREBASE_PROJECT, FIREBASE_COLECCION)

    # 4. Registrar callbacks MQTT y conectar
    if wifi_ok:
        mqtt.registrar_callback(TOPICO_COMANDOS,   on_comando)
        mqtt.registrar_callback(TOPICO_RECONOCIDO, on_reconocido)
        estado["mqtt_ok"] = mqtt.conectar()

    # 5. Lanzar todas las corutinas en paralelo
    print("[Boot] Lanzando corutinas...")
    asyncio.create_task(loop_sensores())
    asyncio.create_task(loop_publicar_mqtt())
    asyncio.create_task(loop_mqtt_recv())
    asyncio.create_task(loop_firebase())

    print("[Boot] Sistema activo. Esperando eventos...\n")

    # Loop principal — mantiene el event loop vivo
    while True:
        await asyncio.sleep(1)


# Punto de entrada
try:
    asyncio.run(main())
except KeyboardInterrupt:
    print("\n[Sistema] Detenido por el usuario.")
except Exception as e:
    print(f"\n[Sistema] Error crítico: {e} — reiniciando en 3 s...")
    sleep(3)
    reset()
