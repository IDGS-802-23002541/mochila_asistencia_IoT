# =============================================================================
# PROYECTO   : Safe-Path AI — Sistema de Navegación Aumentada
# ARCHIVO    : dispositivos.py
# DESCRIPCIÓN: Biblioteca HAL (Hardware Abstraction Layer) para gestión
#              unificada de sensores y actuadores.
#              Recicla y evoluciona las librerías hcsr04.py, imu.py y bocina.py
#              del proyecto SmartCap (LosConriquez, ITL 2024).
# INTEGRANTES: [Nombres del equipo Safe-Path AI]
# VERSIÓN    : 1.0
# FECHA      : 2025
# =============================================================================
#
# PRINCIPIO DE DISEÑO (HAL):
#   El main.py NUNCA debe importar machine.Pin directamente.
#   Si mañana se cambia el HC-SR04 por un LiDAR, main.py no toca ni una línea.
#
# DEPENDENCIAS EXTERNAS (copiar a la ESP32):
#   hcsr04.py  — driver ultrasónico (reciclado de SmartCap)
#   imu.py     — driver MPU6050     (reciclado de SmartCap)
#   vector3d.py— soporte imu.py     (reciclado de SmartCap)
# =============================================================================

from machine import Pin, ADC, SoftI2C, DAC, PWM
from utime import ticks_ms, ticks_diff, sleep_us
import time
import gc

# -- drivers reciclados de SmartCap --
from hcsr04 import HCSR04
from imu import MPU6050


# ─────────────────────────────────────────────────────────────────────────────
# CLASE: SensorBox
# Responsabilidad: encapsular la lectura de HC-SR04, LDR y MPU6050.
# Ningún código externo a esta clase debe conocer pines ni registros I2C.
# ─────────────────────────────────────────────────────────────────────────────
class SensorBox:
    """
    Caja de sensores del Safe-Path AI.

    Sensores integrados:
        - HC-SR04  : distancia frontal en cm   (reciclado de SmartCap)
        - LDR      : detección de baja luz (ADC)
        - MPU6050  : acelerómetro + giroscopio  (reciclado de SmartCap)

    Parámetros de constructor (todos con valores por defecto para la
    ESP32-CAM con pines disponibles):
        pin_trigger  (int): GPIO trigger HC-SR04      — default 12
        pin_echo     (int): GPIO echo HC-SR04          — default 13
        pin_ldr      (int): GPIO ADC del LDR           — default 34
        pin_scl      (int): GPIO SCL SoftI2C MPU6050   — default 15
        pin_sda      (int): GPIO SDA SoftI2C MPU6050   — default 14
        muestras_us  (int): promedio móvil ultrasónico — default 5
        umbral_ldr   (int): 0-4095, debajo = oscuro    — default 2000
        umbral_caida (float): módulo accel en g        — default 2.0
    """

    # Umbrales por defecto — pueden re-configurarse en tiempo de ejecución
    UMBRAL_LDR_DEFAULT   = 2000   # valor ADC (0-4095); menor = oscuro
    UMBRAL_CAIDA_DEFAULT = 2.0    # g; SmartCap usó IMPACTO_THRESHOLD=1.5

    def __init__(self,
                 pin_trigger=12, pin_echo=13,
                 pin_ldr=34,
                 pin_scl=15, pin_sda=14,
                 muestras_us=5,
                 umbral_ldr=UMBRAL_LDR_DEFAULT,
                 umbral_caida=UMBRAL_CAIDA_DEFAULT):

        # ── Ultrasónico HC-SR04 (driver reciclado de SmartCap) ──────────────
        self._ultrasonico = HCSR04(trigger_pin=pin_trigger, echo_pin=pin_echo)
        self._muestras_us = muestras_us

        # ── LDR (ADC) ────────────────────────────────────────────────────────
        self._ldr = ADC(Pin(pin_ldr))
        self._ldr.atten(ADC.ATTN_11DB)   # rango completo 0-3.3 V
        self._umbral_ldr = umbral_ldr

        # ── MPU6050 (driver reciclado de SmartCap) ───────────────────────────
        i2c = SoftI2C(scl=Pin(pin_scl), sda=Pin(pin_sda))
        self._mpu = MPU6050(i2c)
        self._umbral_caida = umbral_caida

        # ── Historial LDR para suavizado (ventana de 3) ──────────────────────
        self._ldr_buffer = [0, 0, 0]
        self._ldr_idx = 0

        print("[SensorBox] Inicializado correctamente.")

    # ── Método público 1: HC-SR04 ────────────────────────────────────────────
    def leer_distancia_cm(self):
        """
        Realiza N lecturas del ultrasónico y devuelve el promedio.
        Descarta lecturas None (fuera de rango).

        Devuelve: float con distancia en cm, o None si todas fallan.

        NOTA PEDAGÓGICA:
            Se promedian 5 muestras (muestras_us=5) para evitar que
            un spike de ruido dispare el motor vibrador sin razón.
            SmartCap usaba lectura directa; aquí aplicamos filtro.
        """
        lecturas = []
        for _ in range(self._muestras_us):
            try:
                d = self._ultrasonico.distance_cm()
                if d is not None and 2.0 <= d <= 400.0:
                    lecturas.append(d)
            except OSError:
                pass
            sleep_us(500)  # pequeña pausa entre pulsos

        if not lecturas:
            return None
        return sum(lecturas) / len(lecturas)

    # ── Método público 2: LDR ────────────────────────────────────────────────
    def esta_oscuro(self, umbral=None):
        """
        Lee el ADC del LDR y aplica un suavizado de ventana 3
        para reducir el ruido del ADC de la ESP32.

        Devuelve: True si la luz es menor al umbral (oscuro), False si hay luz.

        Parámetro:
            umbral (int | None): si None, usa el umbral configurado en el constructor.

        NOTA PEDAGÓGICA:
            El ruido del ADC en la ESP32 puede hacer saltar el valor
            ±200 cuentas aunque la luz sea constante.
            La ventana deslizante de 3 muestras estabiliza la lectura.
        """
        umbral_efectivo = umbral if umbral is not None else self._umbral_ldr

        # actualizar buffer circular
        self._ldr_buffer[self._ldr_idx] = self._ldr.read()
        self._ldr_idx = (self._ldr_idx + 1) % 3
        promedio_ldr = sum(self._ldr_buffer) // 3

        return promedio_ldr < umbral_efectivo

    # ── Método público 3: MPU6050 ────────────────────────────────────────────
    def detectar_caida(self):
        """
        Lee el acelerómetro MPU6050 y calcula el módulo de la aceleración.
        Devuelve True si el módulo supera el umbral (caída / impacto).

        Devuelve: bool

        DISEÑO:
            a_total = sqrt(ax² + ay² + az²)
            En reposo → a_total ≈ 1.0 g (solo gravedad).
            En caída libre → a_total ≈ 0.0 g.
            Al impactar → a_total >> 1.0 g.
            Umbral default = 2.0 g  (ajustable en constructor).

        NOTA PEDAGÓGICA:
            SmartCap usó IMPACTO_THRESHOLD=1.5 g para la gorra.
            Safe-Path AI usa 2.0 g porque la mochila tiene más masa
            y pequeños golpes al caminar no deben disparar alarma.
        """
        try:
            ax, ay, az = self._mpu.accel.xyz
            a_total = (ax**2 + ay**2 + az**2) ** 0.5
            return a_total > self._umbral_caida
        except Exception as e:
            print("[SensorBox] Error MPU6050:", e)
            return False

    # ── Método público 4: resumen global ─────────────────────────────────────
    def obtener_resumen_global(self):
        """
        Devuelve un diccionario con el estado de todos los sensores.
        Útil para construir un único mensaje MQTT con todo el contexto.

        Estructura del diccionario:
        {
            "distancia_cm" : float | None,
            "oscuro"       : bool,
            "caida"        : bool,
            "temperatura"  : float   (del MPU6050, indicativa)
        }
        """
        return {
            "distancia_cm": self.leer_distancia_cm(),
            "oscuro"      : self.esta_oscuro(),
            "caida"       : self.detectar_caida(),
            "temperatura" : self._mpu.temperature,
        }

    # ── Propiedad de acceso al MPU (por si el Firmware Lead necesita giroscopio)
    @property
    def mpu(self):
        """Acceso directo al objeto MPU6050 para uso avanzado."""
        return self._mpu


# ─────────────────────────────────────────────────────────────────────────────
# CLASE: ActuatorBox
# Responsabilidad: encapsular todos los actuadores del casco/mochila.
# ─────────────────────────────────────────────────────────────────────────────
class ActuatorBox:
    """
    Caja de actuadores del Safe-Path AI.

    Actuadores integrados:
        - DFPlayer Mini : reproducción de voz (guía cognitiva)
        - Motor vibrador: alerta háptica de proximidad
        - Buzzer activo : alerta crítica sonora

    Parámetros de constructor:
        pin_motor_vib (int): GPIO motor vibrador     — default 4  (ESP32-CAM GPIO4)
        pin_buzzer    (int): GPIO buzzer activo       — default 2
        pin_dfplayer_tx (int): UART TX → DFPlayer RX — default 17
        pin_dfplayer_rx (int): UART RX ← DFPlayer TX — default 16
        volumen_df    (int): volumen DFPlayer 0-30    — default 20
    """

    # Comandos DFPlayer Mini (protocolo serie propio)
    _DF_START      = 0x7E
    _DF_VERSION    = 0xFF
    _DF_LEN        = 0x06
    _DF_END        = 0xEF
    _DF_CMD_PLAY   = 0x0F
    _DF_CMD_VOL    = 0x06
    _DF_CMD_STOP   = 0x16

    # Mapa de pistas de audio (número de archivo en la tarjeta SD)
    PISTA_OBSTACULO_CERCA  = 1
    PISTA_CAIDA_DETECTADA  = 2
    PISTA_LUZ_BAJA         = 3
    PISTA_PERSONA_CONOCIDA = 4  # prefijo; pista completa = 4 + id_persona
    PISTA_DESCONOCIDO      = 9

    def __init__(self,
                 pin_motor_vib=4,
                 pin_buzzer=2,
                 pin_dfplayer_tx=17,
                 pin_dfplayer_rx=16,
                 volumen_df=20):

        # ── Motor vibrador ────────────────────────────────────────────────────
        self._motor = Pin(pin_motor_vib, Pin.OUT)
        self._motor.value(0)

        # ── Buzzer activo ─────────────────────────────────────────────────────
        self._buzzer = Pin(pin_buzzer, Pin.OUT)
        self._buzzer.value(0)

        # ── DFPlayer Mini via UART ────────────────────────────────────────────
        # NOTA: machine.UART no está disponible en todas las variantes
        # de MicroPython para ESP32-CAM. Se usa import lazy para no romper
        # en placas sin UART libre.
        try:
            from machine import UART
            self._uart = UART(2,
                              baudrate=9600,
                              tx=Pin(pin_dfplayer_tx),
                              rx=Pin(pin_dfplayer_rx))
            self._df_disponible = True
            time.sleep(0.5)
            self._df_set_volumen(volumen_df)
        except Exception as e:
            print("[ActuatorBox] DFPlayer no disponible:", e)
            self._df_disponible = False

        # Estado interno para evitar solapamiento de alertas
        self._ultima_vibracion = 0
        self._ultima_alerta    = 0

        print("[ActuatorBox] Inicializado correctamente.")

    # ── DFPlayer: comando interno ─────────────────────────────────────────────
    def _df_cmd(self, cmd, param_hi=0x00, param_lo=0x00):
        """
        Envía un comando al DFPlayer Mini por UART.
        Protocolo: [0x7E][0xFF][0x06][CMD][0x00][P_HI][P_LO][CHK_HI][CHK_LO][0xEF]
        """
        if not self._df_disponible:
            return
        suma = -(self._DF_VERSION + self._DF_LEN + cmd + 0x00 + param_hi + param_lo)
        chk_hi = (suma >> 8) & 0xFF
        chk_lo = suma & 0xFF
        paquete = bytes([
            self._DF_START, self._DF_VERSION, self._DF_LEN,
            cmd, 0x00, param_hi, param_lo,
            chk_hi, chk_lo, self._DF_END
        ])
        self._uart.write(paquete)

    def _df_set_volumen(self, nivel):
        """Ajusta el volumen del DFPlayer (0-30)."""
        nivel = max(0, min(30, nivel))
        self._df_cmd(self._DF_CMD_VOL, 0x00, nivel)

    # ── Método público 1: DFPlayer ────────────────────────────────────────────
    def reproducir_audio(self, num_pista):
        """
        Reproduce una pista de audio por número (1-255) en el DFPlayer.

        Parámetro:
            num_pista (int): número de pista en la tarjeta SD (carpeta /01/ etc.)

        Si el DFPlayer no está disponible, imprime un mensaje de depuración.
        """
        if self._df_disponible:
            self._df_cmd(self._DF_CMD_PLAY, 0x00, num_pista)
        else:
            print(f"[ActuatorBox] Audio solicitado: pista {num_pista} (DFPlayer no disponible)")

    # ── Método público 2: motor vibrador ─────────────────────────────────────
    def activar_vibracion(self, duracion_ms=300, cooldown_ms=500):
        """
        Activa el motor vibrador durante duracion_ms milisegundos.
        El parámetro cooldown_ms evita activaciones continuas que
        agoten la batería y resulten molestas para el usuario.

        Parámetros:
            duracion_ms  (int): duración del pulso háptico en ms  — default 300
            cooldown_ms  (int): tiempo mínimo entre pulsos en ms  — default 500
        """
        ahora = ticks_ms()
        if ticks_diff(ahora, self._ultima_vibracion) < cooldown_ms:
            return   # aún en periodo de silencio
        self._motor.value(1)
        time.sleep_ms(duracion_ms)
        self._motor.value(0)
        self._ultima_vibracion = ticks_ms()

    def detener_vibracion(self):
        """Apaga el motor vibrador de forma inmediata."""
        self._motor.value(0)

    # ── Método público 3: buzzer crítico ──────────────────────────────────────
    def alerta_critica(self, pulsos=3, duracion_ms=200, cooldown_ms=2000):
        """
        Emite N pulsos del buzzer activo para colisión inminente.
        Es la alerta más urgente del sistema.

        Parámetros:
            pulsos      (int): número de pitidos — default 3
            duracion_ms (int): duración cada pitido en ms — default 200
            cooldown_ms (int): tiempo mínimo entre llamadas — default 2000
        """
        ahora = ticks_ms()
        if ticks_diff(ahora, self._ultima_alerta) < cooldown_ms:
            return
        for _ in range(pulsos):
            self._buzzer.value(1)
            time.sleep_ms(duracion_ms)
            self._buzzer.value(0)
            time.sleep_ms(duracion_ms)
        self._ultima_alerta = ticks_ms()

    # ── Método público 4: silencio total ─────────────────────────────────────
    def silenciar_todo(self):
        """
        Apaga todos los actuadores de forma inmediata.
        Útil en caso de emergencia o al entrar en modo reposo.
        """
        self._motor.value(0)
        self._buzzer.value(0)
        if self._df_disponible:
            self._df_cmd(self._DF_CMD_STOP)
        print("[ActuatorBox] Todos los actuadores silenciados.")


# ─────────────────────────────────────────────────────────────────────────────
# CLASE: MQTTManager
# Responsabilidad: encapsular toda la lógica de conexión, reconexión y
# publicación MQTT, separándola del firmware principal.
# Reciclado y mejorado de la lógica MQTT de SmartCapFinal.py
# ─────────────────────────────────────────────────────────────────────────────
class MQTTManager:
    """
    Gestor de comunicación MQTT para Safe-Path AI.

    Abstrae MQTTClient para que main.py solo llame:
        mqtt.publicar(topico, mensaje)
        mqtt.verificar_mensajes()

    Parámetros de constructor:
        broker    (str) : IP o hostname del broker
        puerto    (int) : puerto TCP (default 1883)
        usuario   (str) : usuario MQTT
        contrasena(str) : contraseña MQTT
        client_id (str) : identificador único del cliente
    """

    def __init__(self, broker, puerto=1883, usuario="", contrasena="",
                 client_id="safepath_client"):
        self._broker    = broker
        self._puerto    = puerto
        self._usuario   = usuario
        self._contrasena = contrasena
        self._client_id = client_id
        self._cliente   = None
        self._conectado = False
        self._callbacks = {}   # topico → función callback

    def registrar_callback(self, topico, funcion):
        """
        Asocia una función Python al tópico MQTT indicado.
        La función recibe (topico_str, mensaje_str).

        Ejemplo:
            mqtt.registrar_callback("safepath/cmd", mi_funcion)
        """
        self._callbacks[topico] = funcion

    def conectar(self):
        """
        Establece la conexión con el broker y suscribe a los tópicos
        registrados con registrar_callback().

        Devuelve: True si conectó correctamente, False si falló.
        """
        try:
            from umqtt.simple import MQTTClient
            self._cliente = MQTTClient(
                self._client_id, self._broker,
                user=self._usuario, password=self._contrasena,
                port=self._puerto
            )
            self._cliente.set_callback(self._dispatcher)
            self._cliente.connect()
            for topico in self._callbacks:
                self._cliente.subscribe(topico.encode())
            self._conectado = True
            print(f"[MQTTManager] Conectado a {self._broker}:{self._puerto}")
            return True
        except Exception as e:
            print("[MQTTManager] Error al conectar:", e)
            self._conectado = False
            return False

    def _dispatcher(self, topico_bytes, msg_bytes):
        """Enruta mensajes entrantes al callback correcto."""
        topico = topico_bytes.decode()
        mensaje = msg_bytes.decode()
        if topico in self._callbacks:
            try:
                self._callbacks[topico](topico, mensaje)
            except Exception as e:
                print(f"[MQTTManager] Error en callback '{topico}':", e)

    def publicar(self, topico, mensaje):
        """
        Publica mensaje (str) en el tópico indicado.
        Si no hay conexión, intenta reconectar una vez.

        Devuelve: True si publicó, False si falló.
        """
        if not self._conectado:
            self.conectar()
        try:
            self._cliente.publish(topico.encode(), mensaje.encode())
            return True
        except Exception as e:
            print("[MQTTManager] Error al publicar:", e)
            self._conectado = False
            return False

    def verificar_mensajes(self):
        """
        Llama a check_msg() del broker. Debe invocarse periódicamente
        en el loop principal (o en una corutina asyncio).
        """
        if self._conectado:
            try:
                self._cliente.check_msg()
            except Exception as e:
                print("[MQTTManager] Error al verificar mensajes:", e)
                self._conectado = False

    @property
    def conectado(self):
        """Bool — True si la sesión MQTT está activa."""
        return self._conectado


# ─────────────────────────────────────────────────────────────────────────────
# CLASE: FirebaseClient
# Responsabilidad: enviar registros de eventos a Firestore REST API.
# Reciclado y modularizado de SmartCapFinal.py → enviar_datos_firebase()
# ─────────────────────────────────────────────────────────────────────────────
class FirebaseClient:
    """
    Cliente mínimo para Firestore REST API desde MicroPython.

    Parámetros de constructor:
        api_key       (str): clave API de Firebase
        project_id    (str): ID del proyecto en GCP
        coleccion     (str): nombre de la colección Firestore
    """

    def __init__(self, api_key, project_id, coleccion):
        self._api_key    = api_key
        self._project_id = project_id
        self._coleccion  = coleccion
        self._url = (
            f"https://firestore.googleapis.com/v1/projects/{project_id}"
            f"/databases/(default)/documents/{coleccion}?key={api_key}"
        )

    def enviar_evento(self, datos_dict):
        """
        Envía un diccionario de datos como nuevo documento a Firestore.

        Los tipos soportados en datos_dict son: str, int, float, bool.
        Cualquier otro tipo se convierte a str automáticamente.

        Devuelve: True si el servidor respondió 200, False si hubo error.
        """
        import urequests
        import json

        # Construir estructura de campos Firestore
        campos = {}
        for clave, valor in datos_dict.items():
            if isinstance(valor, bool):
                campos[clave] = {"booleanValue": valor}
            elif isinstance(valor, int):
                campos[clave] = {"integerValue": str(valor)}
            elif isinstance(valor, float):
                campos[clave] = {"doubleValue": valor}
            elif valor is None:
                campos[clave] = {"nullValue": None}
            else:
                campos[clave] = {"stringValue": str(valor)}

        cuerpo = json.dumps({"fields": campos})
        try:
            headers = {"Content-Type": "application/json"}
            resp = urequests.post(self._url, data=cuerpo, headers=headers)
            ok = (resp.status_code == 200)
            resp.close()
            gc.collect()
            return ok
        except Exception as e:
            print("[FirebaseClient] Error al enviar:", e)
            return False
