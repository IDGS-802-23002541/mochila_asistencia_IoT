# =============================================================================
# PROYECTO   : Vision Guard — Sistema de Navegación Aumentada
# ARCHIVO    : main.py (Firmware Central de Control IoT de Producción)
# DESCRIPCIÓN: Controlador asíncrono que orquesta en paralelo la inicialización
#              vía BLE, detección de eventos de catálogo (Caída, Obstáculos),
#              memoria de ruta y cierre seguro a través del botón BOOT (GPIO 0).
# VERSIÓN    : 3.2 (Eliminación comunicación UART con app_movil, únicamente se 
#              subscribe y publica a los tópicos. Se arregla la comunicación Bluethoot)
# =============================================================================

import uasyncio as asyncio
import network
import json
import gc
import ubinascii
import utime
import math
import bluetooth
import struct
from time import sleep, time
from machine import Pin, reset, unique_id

from dispositivos import SensorBox, ActuatorBox, MQTTManager
from gps_manager  import GPSManager
from led_rgb import LedRGBManager

# ─────────────────────────────────────────────────────────────────────────────
# CONFIGURACIÓN OPERATIVA (Ajustada con WiFi local y Broker HiveMQ)
# ─────────────────────────────────────────────────────────────────────────────
REDES_WIFI = [
    ("INFINITUM8536_2.4", "4696601711"),
    ("POCO_X7_Pro", "123goner456789"),
    ("Catasi", "papaya10"),
    ("CATA", "papantla"), 
]

# Configuración del Broker de Diego (HiveMQ Cloud SSL en puerto 8883)
MQTT_BROKER    = "4ff222212d4746d0a5541cb27f96f5aa.s1.eu.hivemq.cloud"
MQTT_PUERTO    = 8883
MQTT_USUARIO   = "diegosa9_"
MQTT_PASSWORD  = "Diegosa9"
MQTT_CLIENT_ID = "vision_guard"

# Tópicos MQTT
TOPICO_TELEMETRIA = "cangurera/telemetria"
TOPICO_EVENTOS    = "cangurera/eventos"
TOPICO_FINALIZAR  = "cangurera/recorrido/finalizar"
TOPICO_COMANDOS   = "cangurera/comandos"
# De TOPICO_ESCUCHA se reciben eventos push del backend, con formato:
# {
#     "macAddress": "IEE2-..",
#     "mensaje": "acercandose_zona_caliente",
#     "tipoEventoid": 3,
#     "latitud": 21.22,
#     "longitud": -101.2,
#     "distanciaMetros": 42.5
# }

# Configuración del GPS (UART2)
GPS_UART_ID = 2
GPS_PIN_TX  = 17
GPS_PIN_RX  = 16
GPS_LAT_DEF = 00.000 
GPS_LON_DEF = -00.000 

# Umbrales operacionales y tiempos de muestreo
DISTANCIA_ALERTA_FRONTAL_CM = 100.0  # Alerta por debajo de 1 metro
INTERVALO_ALERTAS_VOZ_MS    = 3000   # Bloqueo de 3 segundos para el altavoz
INTERVALO_MUESTREO_GPS_S    = 10     # Almacenamiento de ruta cada 10 segundos
INTERVALO_TELEMETRIA_S      = 5      # Frecuencia de envío de telemetría periódica

# ─────────────────────────────────────────────────────────────────────────────
# CATÁLOGO DE EVENTOS (Fuente única de verdad — sincronizado con backend)
# Id | NombreEvento      | Severidad
#  1 | Trafico           | Media
#  2 | Obstaculo         | Baja
#  4 | Caida_Detectada   | Critica
# ─────────────────────────────────────────────────────────────────────────────
CATALOGO_EVENTOS = {
    1: {"nombre": "Trafico",         "severidad": "Media",   "pista": None},  # pista asignada dinámicamente (lateral/frontal)
    2: {"nombre": "Obstaculo",       "severidad": "Baja",    "pista": None},
    4: {"nombre": "Caida_Detectada", "severidad": "Critica", "pista": None},
}

# ─────────────────────────────────────────────────────────────────────────────
# ESTADO GLOBAL COMPARTIDO
# ─────────────────────────────────────────────────────────────────────────────
estado = {
    "wifi_ok"         : False,
    "mqtt_ok"         : False,
    "silenciado"      : False,
    "recorrido_id"    : None,   # Se reciben desde el broker MQTT por medio de la app móvil
    "recorrido_activo": False,  # True en cuanto se recibe el RecorridoId
    "solicitud_cierre": False,  # Bandera para finalizar trayecto vía app móvil
    "ruta_coordenadas": [],     # Array en memoria que almacena el trayecto
    "ultimo_resumen"  : {},
    "ultima_pos_gps"  : {},
    "vinculado": False,
}

# Nombre ESP32 para la vinculación bluethoot
BLE_NOMBRE = "vision_guard_esp32"
ble = None

# UUIDs del servicio BLE (solo para identificación)
UUID_SERVICIO = bluetooth.UUID("12345678-1234-5678-1234-56789abcdef0")
UUID_CARACTERISTICA = bluetooth.UUID("12345678-1234-5678-1234-56789abcdef1")

_FLAG_READ = bluetooth.FLAG_READ

# Configuración del Botón Físico de Cierre (Botón BOOT / GPIO 0 en ESP32 es Active LOW)
boton_finalizar = Pin(0, Pin.IN, Pin.PULL_UP)

# ─────────────────────────────────────────────────────────────────────────────
# AUXILIAR: MAC Address única del dispositivo (formato "AA:BB:CC:DD:EE:FF")
# ─────────────────────────────────────────────────────────────────────────────
def obtener_mac_address():
    """Obtiene la dirección MAC de la interfaz WiFi STA como identificador único."""
    try:
        wlan = network.WLAN(network.STA_IF)
        mac_bytes = wlan.config('mac')
        mac_hex = ubinascii.hexlify(mac_bytes).decode('utf-8').upper()
        return ":".join(mac_hex[i:i+2] for i in range(0, 12, 2))
    except Exception as e:
        print("[MAC] No se pudo leer la MAC de WiFi, usando unique_id():", e)
        uid_hex = ubinascii.hexlify(unique_id()).decode('utf-8').upper()
        return "ESP32-" + uid_hex

# ─────────────────────────────────────────────────────────────────────────────
# AUXILIAR: Generación de Timestamps en formato ISO 8601 UTC
# ─────────────────────────────────────────────────────────────────────────────
def obtener_timestamp_iso():
    """Genera una cadena de tiempo formateada en formato estándar UTC."""
    tm = utime.localtime()
    return "{:04d}-{:02d}-{:02d}T{:02d}:{:02d}:{:02d}Z".format(
        tm[0], tm[1], tm[2], tm[3], tm[4], tm[5]
    )

def obtener_timestamp_unix():
    """Devuelve el timestamp Unix actual (segundos desde epoch)."""
    return int(time())

# -----------------------------------------------------------------------------
# BLE - Servidor GATT para vinculación
# -----------------------------------------------------------------------------

_IRQ_CENTRAL_CONNECT = 1
_IRQ_CENTRAL_DISCONNECT = 2

ble = None
conexion = None
handle_info = None


def advertising_payload(nombre):
    nombre = nombre.encode()
    payload = bytearray()
    # Flags
    payload += struct.pack("BB", 2, 0x01)
    payload += bytes([0x06])
    # Nombre completo
    payload += struct.pack("BB", len(nombre) + 1, 0x09)
    payload += nombre
    return payload

def iniciar_advertising():
    payload = advertising_payload(BLE_NOMBRE)
    ble.gap_advertise(
        100000,
        adv_data=payload
    )
    print(f"[BLE] Publicando publicidad BLE como '{BLE_NOMBRE}'")

def ble_irq(event, data):
    global conexion
    if event == _IRQ_CENTRAL_CONNECT:
        conexion, _, _ = data
        print("[BLE] Celular conectado.")
        led.estado_vinculado()
    elif event == _IRQ_CENTRAL_DISCONNECT:
        conexion = None
        print("[BLE] Celular desconectado.")
        iniciar_advertising()

def inicializar_ble():
    global ble
    global handle_info

    ble = bluetooth.BLE()
    ble.active(True)
    ble.irq(ble_irq)

    SERVICIO = (UUID_SERVICIO,((UUID_CARACTERISTICA,_FLAG_READ,),),)

    ((handle_info,),) = ble.gatts_register_services((SERVICIO,))

    ble.gatts_write(handle_info,b"Vision Guard")

    iniciar_advertising()
    print("[BLE] Servicio GATT registrado correctamente.")

#
# ─────────────────────────────────────────────────────────────────────────────
# CONEXIÓN A LA RED WIFI
# ─────────────────────────────────────────────────────────────────────────────
async def conectar_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    for ssid, pwd in REDES_WIFI:
        print(f"[WiFi] Buscando red local: {ssid}")
        wlan.connect(ssid, pwd)
        for _ in range(15):
            if wlan.isconnected():
                print(f"[WiFi] Conexión establecida. IP: {wlan.ifconfig()[0]}")
                estado["wifi_ok"] = True
                return True
            await asyncio.sleep(1)
        wlan.disconnect()
        await asyncio.sleep(0.5)
    print("[WiFi] Sin conexión WiFi. Operando de forma local (Offline-Ready)")
    return False

# ─────────────────────────────────────────────────────────────────────────────
# PROCESAMIENTO DE COMANDOS REMOTOS (MQTT) — Tópico 'cangurera/comandos'
# ─────────────────────────────────────────────────────────────────────────────
def on_comando(topico, mensaje):
    print(f"[MQTT] Comando recibido: {mensaje}")
    try:
        datos = json.loads(mensaje)
    except Exception as e:
        print("[MQTT] JSON inválido:", e)
        return
    accion = datos.get("accion")

    if accion == "vincular":
        estado["vinculado"] = True
        asyncio.create_task(led.parpadear_azul())
        print("[LED] Mochila vinculada correctamente.")
        return
    
    mac = datos.get("macAddress")
    print("MAC recibida :", mac)
    print("MAC ESP32    :", obtener_mac_address())

    if mac != obtener_mac_address():
        print("MAC diferente, ignorando comando")
        return
    if accion == "iniciar":
        if estado["recorrido_activo"]:
            print("[Sistema] Ya existe un recorrido activo.")
            return
        recorrido = datos.get("recorridoId")
        if recorrido is None:
            print("[MQTT] recorridoId inexistente.")
            return
        estado["recorrido_id"] = recorrido
        estado["recorrido_activo"] = True
        asyncio.create_task(led.parpadear_verde())
        estado["ruta_coordenadas"] = []
        print(f"[Sistema] Recorrido {recorrido} iniciado.")
        actuadores.reproducir_audio(5)
    if accion == "detener":
        estado["solicitud_cierre"] = True
        print("[Sistema] Solicitud de finalización recibida.")
    elif accion == "desvincular":
        estado["vinculado"] = False
        led.apagar()
        print("[Sistema] Mochila desvinculada.")

# ─────────────────────────────────────────────────────────────────────────────
# PROCESAMIENTO DE EVENTOS PULL DESDE BACKEND — Tópico 'cangurera/pull'
# ─────────────────────────────────────────────────────────────────────────────
# def on_pull_evento(topico, mensaje):
#     """
#     Procesa los eventos enviados por el backend y los almacena para que sean
#     gestionados por el ciclo principal del firmware (loop_sensores).
#     """
#     print(f"[MQTT-Pull] Mensaje recibido: {mensaje}")
#     try:
#         datos = json.loads(mensaje)
#     except Exception as e:
#         print("[MQTT-Pull] Error: el payload recibido no es un JSON válido:", e)
#         return

#     # Validar que el mensaje esté dirigido a este dispositivo específico
#     mac_recibida = datos.get("macAddress")
#     mac_propia   = obtener_mac_address()

#     if mac_recibida != mac_propia:
#         print(f"[MQTT-Pull] Mensaje ignorado: MAC destino ({mac_recibida}) no coincide con este dispositivo ({mac_propia}).")
#         return

#     # Validar recorrido activo
#     recorrido_id = datos.get("recorridoId")

#     if recorrido_id != estado["recorrido_id"]:
#         print("[MQTT-Pull] Mensaje descartado: recorrido no coincide.")
#         return
    
#     tipo_evento_id = datos.get("tipoEventoid")
#     texto_mensaje  = datos.get("mensaje", "")
#     distancia_m    = datos.get("distanciaMetros")

#     if tipo_evento_id not in CATALOGO_EVENTOS:
#         print(f"[MQTT-Pull] Tipo de evento desconocido: {tipo_evento_id}")
#         return
    
#     estado["evento_pull_pendiente"] = {
#         "tipoEventoid": tipo_evento_id,
#         "mensaje": datos.get("mensaje", ""),
#         "distanciaMetros": datos.get("distanciaMetros"),
#         "timestamp": obtener_timestamp_unix()
#     }

#     print(f"[MQTT-Pull] Evento válido recibido -> Id: {tipo_evento_id} | "
#           f"Nombre: {info_evento['nombre']} | Severidad: {info_evento['severidad']} | "
#           f"Mensaje: '{texto_mensaje}' | Distancia: {distancia_m} m")



# ─────────────────────────────────────────────────────────────────────────────
# ENVIAR TELEMETRIA AL BROKER (Tópico 'cangurera/telemetria')
# ─────────────────────────────────────────────────────────────────────────────
def publicar_telemetria():
    """
    Construye y envía el JSON de telemetría periódica del dispositivo:
    posición GPS actual, si es estimada, y timestamp Unix. 
    """
    if not estado["mqtt_ok"]:
        print("[Offline Log] Telemetría no enviada: sin conexión MQTT.")
        return
    
    if not estado["recorrido_activo"]:
        return

    pos = estado.get("ultima_pos_gps", {})
    tiene_fix = pos.get("valido", False)

    payload = {
        "macAddress": obtener_mac_address(),
        "latitud": float(pos.get("lat") or GPS_LAT_DEF),
        "longitud": float(pos.get("lon") or GPS_LON_DEF),
        "geoEsEstimado": not tiene_fix,
        "fecha": obtener_timestamp_unix(),
    }

    try:
        msg = json.dumps(payload)
        mqtt.publicar(TOPICO_TELEMETRIA, msg)
        print(f"[MQTT] Telemetría enviada: {msg}")
    except Exception as e:
        print("[MQTT] Error al publicar telemetría:", e)


# ─────────────────────────────────────────────────────────────────────────────
# ENVIAR EVENTO AL BROKER (Tópico 'cangurera/eventos')
# ─────────────────────────────────────────────────────────────────────────────
def publicar_evento_anomalo(tipo_evento_id, fuerza_g=None):
    """Construye y envía el JSON del evento de forma instantánea si hay conexión."""
    if not estado["recorrido_activo"] or estado["recorrido_id"] is None:
        return

    # Validar contra el catálogo antes de publicar
    if tipo_evento_id not in CATALOGO_EVENTOS:
        print(f"[MQTT] Advertencia: se intentó publicar un tipoEventoId ({tipo_evento_id}) inexistente en el catálogo.")
        return

    pos = estado.get("ultima_pos_gps", {})
    tiene_fix = pos.get("valido", False)
    resumen = estado.get("ultimo_resumen", {})

    payload = {
        "macAddress": obtener_mac_address(),
        "recorridoId": estado["recorrido_id"],
        "tipoEventoId": tipo_evento_id,
        "timeStamp": obtener_timestamp_unix(),
        "latitud": float(pos.get("lat") or GPS_LAT_DEF),
        "longitud": float(pos.get("lon") or GPS_LON_DEF),
        "geoEsEstimado": not tiene_fix, # Estimado (True) si no tiene enlace satelital
        "fuerzaImpactoG": fuerza_g,
        "ir_izq": bool(resumen.get("ir_izq")),
        "ir_der": bool(resumen.get("ir_der")),
        "dist": resumen.get("distancia_cm"),
    }
    
    if estado["mqtt_ok"]:
        msg = json.dumps(payload)
        mqtt.publicar(TOPICO_EVENTOS, msg)
        print(f"[MQTT] Evento {tipo_evento_id} ({CATALOGO_EVENTOS[tipo_evento_id]['nombre']}) enviado: {msg}")
    else:
        print(f"[Offline Log] Evento {tipo_evento_id} guardado localmente: {payload}")

# ─────────────────────────────────────────────────────────────────────────────
# CORUTINA 1 — Control de Sensores e Inteligencia de Eventos Directos
# ─────────────────────────────────────────────────────────────────────────────
async def loop_sensores():
    ultimo_tiempo_alerta_voz = 0
    from utime import ticks_ms, ticks_diff
    
    while True:
        if estado["silenciado"]:
            await asyncio.sleep(0.5)
            continue

        resumen = sensores.obtener_resumen_global()
        estado["ultimo_resumen"] = resumen

        dist = resumen.get("distancia_cm")
        ir_izq = resumen.get("ir_izq")
        ir_der = resumen.get("ir_der")
        caida = resumen.get("caida")  # True si el tropiezo supera 1.5G

        # Alerta acústica si el peligro está a menos de 30 cm
        actuadores.actualizar_alerta_distancia(dist)

        # Activación rápida de la vibración (Motor háptico)
        if (dist is not None and dist <= 50.0) or ir_izq or ir_der or caida:
            actuadores.activar_alerta_haptica()
        else:
            actuadores.desactivar_alerta_haptica()

        # Evaluación de Alertas Físicas por Voz e Inyección Inmediata de Eventos MQTT
        # (Esto solo corre si el usuario está realizando un recorrido activo)
        tiempo_actual = ticks_ms()
        if ticks_diff(tiempo_actual, ultimo_tiempo_alerta_voz) >= INTERVALO_ALERTAS_VOZ_MS:
            
            # Prioridad 1: Impacto/Tropiezo (Catálogo Id 4: Caida_Detectada — Crítica)
            if caida:
                actuadores.reproducir_audio(ActuatorBox.PISTA_CAIDA_DETECTADA)
                # Obtenemos un cálculo de G aproximado
                try:
                    ax, ay, az = sensores._mpu.accel.xyz
                    g_leidos =  math.sqrt(ax**2 + ay**2 + az**2 )/9.80665
                except:
                    g_leidos = 1.5
                publicar_evento_anomalo(tipo_evento_id=4, fuerza_g=round(g_leidos, 2))
                ultimo_tiempo_alerta_voz = tiempo_actual
                await asyncio.sleep(2.0) # Retardo para evitar rebote de impacto

            # Prioridad 2: Obstáculo frontal detectado (Catálogo Id 2: Obstaculo — Baja)
            elif dist is not None and dist <= DISTANCIA_ALERTA_FRONTAL_CM:
                actuadores.reproducir_audio(ActuatorBox.PISTA_OBSTACULO_FRONTAL)
                publicar_evento_anomalo(tipo_evento_id=2)
                ultimo_tiempo_alerta_voz = tiempo_actual

            # Prioridad 3: Obstáculo Lateral Izquierdo (Catálogo Id 2: Obstaculo — Baja)
            elif ir_izq:
                actuadores.reproducir_audio(ActuatorBox.PISTA_OBSTACULO_IZQ)
                publicar_evento_anomalo(tipo_evento_id=2)
                ultimo_tiempo_alerta_voz = tiempo_actual

            # Prioridad 4: Obstáculo Lateral Derecho (Catálogo Id 2: Obstaculo — Baja)
            elif ir_der:
                actuadores.reproducir_audio(ActuatorBox.PISTA_OBSTACULO_DER)
                publicar_evento_anomalo(tipo_evento_id=2)
                ultimo_tiempo_alerta_voz = tiempo_actual

        await asyncio.sleep(0.2)  # Muestreo a alta velocidad (200 ms)

# ─────────────────────────────────────────────────────────────────────────────
# CORUTINA 2 — Monitoreo de Señal GPS e Historial de Ruta (Cada 10 segundos)
# ─────────────────────────────────────────────────────────────────────────────
async def loop_gps_tracker():
    ultimo_tiempo_ruta = 0
    
    while True:
        # Procesamos la UART2 de forma continua sin bloquear el hilo de ejecución
        if gps.leer_uart():
            estado["ultima_pos_gps"] = gps.obtener_posicion()

        ahora = int(time())
        if ahora - ultimo_tiempo_ruta >= INTERVALO_MUESTREO_GPS_S:
            pos = gps.obtener_posicion()
            estado["ultima_pos_gps"] = pos
            
            # Si el recorrido está activo, vamos almacenando la coordenada en memoria
            if estado["recorrido_activo"]:
                coordenada = {
                    "lat": round(pos.get("lat") or GPS_LAT_DEF, 6),
                    "lon": round(pos.get("lon") or GPS_LON_DEF, 6),
                    "ts": obtener_timestamp_iso()
                }
                estado["ruta_coordenadas"].append(coordenada)
                print(f"[Tracker] Posición registrada en ruta ({len(estado['ruta_coordenadas'])} puntos): {coordenada}")
                
                # Nota: Id 5 (GPS Sin Señal) no está en el catálogo activo actual;
                # se conserva el log local pero se omite la publicación MQTT
                # hasta que el evento sea dado de alta oficialmente en el catálogo.
                if not pos.get("valido", False):
                    print("[Tracker] Advertencia local: sin señal GPS válida (evento Id 5 no está en catálogo activo).")

            ultimo_tiempo_ruta = ahora
            
        await asyncio.sleep(0.2)

# ─────────────────────────────────────────────────────────────────────────────
# CORUTINA 3 — Escucha Activa de Mensajes MQTT (Comandos + Pull de eventos)
# ─────────────────────────────────────────────────────────────────────────────
async def loop_mqtt_recv():
    while True:
        if estado["mqtt_ok"]:
            mqtt.verificar_mensajes()
        await asyncio.sleep(0.1)

# ─────────────────────────────────────────────────────────────────────────────
# CORUTINA 5 — Envío Periódico de Telemetría (Cada INTERVALO_TELEMETRIA_S)
# ─────────────────────────────────────────────────────────────────────────────
async def loop_telemetria():
    while True:
        publicar_telemetria()
        await asyncio.sleep(INTERVALO_TELEMETRIA_S)

# ─────────────────────────────────────────────────────────────────────────────
# FUNCIÓN: Cierre y Finalización del Recorrido (Publica en 'cangurera/recorrido/finalizar')
# ─────────────────────────────────────────────────────────────────────────────
async def finalizar_recorrido_actual():
    """
    Empaqueta el historial de coordenadas acumulado, lo publica en una única capa
    de serialización JSON hacia el backend por MQTT y libera la memoria RAM del ESP32.
    """
    print("[Sistema] Iniciando proceso de empaquetado e instanciación de cierre...")
    
    # 1. Forzar limpieza previa de la memoria interna
    gc.collect()
    
    # 2. Validar que tengamos un ID de recorrido asignado antes de enviar
    if not estado.get("recorrido_id"):
        print("[MQTT Error] No se puede finalizar: 'recorrido_id' es nulo o inválido.")
        return False

    # 3. Construir el payload estructurado directamente en un objeto nativo
    # Pasamos 'ruta_coordenadas' como lista directa de Python, NO dobles comillas por string separado
    payload = {
        "macAddress": obtener_mac_address(),
        "recorridoId": estado["recorrido_id"],
        "rutaCoordenadas": estado["ruta_coordenadas"],
        "fechaFin": obtener_timestamp_unix(),
    }
    
    try:
        # 4. Una sola serialización JSON global y limpia
        publicacion_final = json.dumps(payload)
        
        print("[MQTT] Publicando payload unificado en 'cangurera/recorrido/finalizar'...")
        mqtt.publicar(TOPICO_FINALIZAR, publicacion_final)
        
        # 5. Modificar estados de control de ruta de forma segura
        estado["recorrido_activo"] = False
        await led.parpadear_rojo()

        await asyncio.sleep(3)

        if estado["vinculado"]:
            led.estado_vinculado()
        else:
            led.apagar()
        print("[MQTT] ¡Datos enviados con éxito a FastAPI!")
              
        
        # 6. Vaciado radical del historial para evitar fugas de memoria
        estado["ruta_coordenadas"] = []
        estado["recorrido_id"] = None
        gc.collect()
        return True
        
    except MemoryError:
        print("[CRÍTICO] Desbordamiento de memoria (OOM). El historial es demasiado grande.")
        
        # Payload de rescate para que Diego y Damián sepan en el servidor que el trayecto colapsó
        payload_emergencia = {
            "macAddress": obtener_mac_address(),
            "recorridoId": estado["recorrido_id"],
            "rutaCoordenadas": [],
            "fechaFin": obtener_timestamp_unix(),
            "error": "CRITICAL_ESP32_OUT_OF_MEMORY"
        }
        try:
            mqtt.publicar(TOPICO_FINALIZAR, json.dumps(payload_emergencia))
        except:
            print("[CRÍTICO] Falló incluso la publicación de emergencia.")
            
        estado["ruta_coordenadas"] = []
        estado["recorrido_id"] = None
        estado["recorrido_activo"] = False
        gc.collect()
        return False

# ─────────────────────────────────────────────────────────────────────────────
# CORUTINA 4 — Monitoreo del Botón Físico de Cierre (Botón BOOT / GPIO 0)
# ─────────────────────────────────────────────────────────────────────────────
async def loop_boton_finalizar():
    while True:
        # Detectamos pulsación si el valor lógico es 0 (Presionado)
        if boton_finalizar.value() == 0 or estado["solicitud_cierre"]:
            # Filtro anti-rebote eléctrico
            if boton_finalizar.value() == 0:
                await asyncio.sleep(0.05)
                
            if boton_finalizar.value() == 0 or estado["solicitud_cierre"]:
                print("[Hardware] Detención de recorrido activada.")
                estado["solicitud_cierre"] = False
                if estado["recorrido_activo"]:
                    await finalizar_recorrido_actual()
                else:
                    print("[Hardware] El dispositivo está inactivo. Presione el botón solo durante un recorrido.")
                # Esperar hasta que se libere el botón
                while boton_finalizar.value() == 0:
                    await asyncio.sleep(0.1)
        await asyncio.sleep(0.1)

# ─────────────────────────────────────────────────────────────────────────────
# ORQUESTRADOR PRINCIPAL (Arranque del Sistema)
# ─────────────────────────────────────────────────────────────────────────────
async def main():
    global sensores, actuadores, mqtt, gps

    print("=" * 60)
    print("      VISION GUARD — FIRMWARE DE CONTROL CENTRAL v3.2")
    print("      CONFIG: HC-SR04 | MPU6050 | 2x INFRARROJOS | MOTOR | BUZZER")
    print("=" * 60)

    # 1. Instanciación de componentes mediante la HAL (Seguridad de Pines)
    sensores   = SensorBox(umbral_caida=1.5) # Calibrado de tropiezo a 1.5G
    actuadores = ActuatorBox()
    
    # 2. Inicialización del GPS con velocidad de transmisión validada a 115200 bps
    gps        = GPSManager(uart_id=GPS_UART_ID,
                            pin_tx=GPS_PIN_TX,
                            pin_rx=GPS_PIN_RX,
                            baudrate=115200,
                            lat_defecto=GPS_LAT_DEF,
                            lon_defecto=GPS_LON_DEF)

    
    # 3. Conectar Red WiFi local
    wifi_ok = await conectar_wifi()

    # 4. Inicializar clientes de Nube (Diego)
    mqtt = MQTTManager(broker=MQTT_BROKER, puerto=MQTT_PUERTO,
                       usuario=MQTT_USUARIO, contrasena=MQTT_PASSWORD,
                       client_id=MQTT_CLIENT_ID)
    
    # 5. Función estado mochila por led rgb
    global led 
    led = LedRGBManager()
    led.apagar()

    # Inicializar BLE
    inicializar_ble()

    # 6. Configurar callbacks de comandos, pull de eventos, e iniciar Broker
    if wifi_ok:
        mqtt.registrar_callback(TOPICO_COMANDOS, on_comando)
        estado["mqtt_ok"] = mqtt.conectar()
        if estado["mqtt_ok"]:
            print("[MQTT] Broker conectado correctamente.")
           

    # 7. Ejecución del pool de tareas en paralelo
    print("[Boot] Iniciando sistema de tareas asíncronas...")
    asyncio.create_task(loop_sensores())
    asyncio.create_task(loop_gps_tracker())
    asyncio.create_task(loop_mqtt_recv())
    asyncio.create_task(loop_boton_finalizar())
    asyncio.create_task(loop_telemetria())

    print("[Boot] Vision Guard operando de forma asíncrona exitosamente.\n")

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