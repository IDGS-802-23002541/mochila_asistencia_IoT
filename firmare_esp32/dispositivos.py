# =============================================================================
# PROYECTO   : Vision Guard
# ARCHIVO    : dispositivos.py (Versión con Infrarrojos, Motor y Buzzer)
# DESCRIPCIÓN: Biblioteca HAL (Hardware Abstraction Layer) para gestión
#              unificada de sensores y actuadores optimizados para ESP32.
# VERSIÓN    : 2.4 (Resolución de conflicto UART1/UART2 y checksum del DFPlayer)
# =============================================================================

from machine import Pin, SoftI2C
from utime import ticks_ms, ticks_diff, sleep_us
import time
import gc

# Drivers importados del proyecto base
from hcsr04 import HCSR04
from imu import MPU6050


# ─────────────────────────────────────────────────────────────────────────────
# CLASE: SensorBox (Gestor de entradas físicas)
# ─────────────────────────────────────────────────────────────────────────────
class SensorBox:
    """
    Abstrae los sensores del sistema Safe-Path.
    Ningún script externo a esta clase debe conocer pines ni registros.
    """

    UMBRAL_CAIDA_DEFAULT = 1.5  # Fuerza G para disparar alerta de caída (2.5G)

    def __init__(self,
                 pin_trigger=12, pin_echo=13,
                 pin_ir_izq=14, pin_ir_der=27,
                 pin_scl=22, pin_sda=21,
                 muestras_us=5,
                 umbral_caida=UMBRAL_CAIDA_DEFAULT):

        # 1. Sensor Ultrasónico HC-SR04
        self._ultrasonico = HCSR04(trigger_pin=pin_trigger, echo_pin=pin_echo)
        self._muestras_us = muestras_us

        # 2. Sensores Infrarrojos Laterales (FC-51)
        # Se configuran con resistencia Pull-Up interna (Active LOW)
        self._ir_izq = Pin(pin_ir_izq, Pin.IN, Pin.PULL_UP)
        self._ir_der = Pin(pin_ir_der, Pin.IN, Pin.PULL_UP)

        # 3. Acelerómetro MPU6050
        try:
            i2c = SoftI2C(scl=Pin(pin_scl), sda=Pin(pin_sda))
            self._mpu = MPU6050(i2c)
            self._mpu_ok = True
        except Exception as e:
            print("[SensorBox] Error al inicializar MPU6050:", e)
            self._mpu_ok = False
            
        self._umbral_caida = umbral_caida
        print("[SensorBox] Inicializado en modo ESP32 Estándar.")

    def leer_distancia_cm(self):
        """Realiza N lecturas promediadas para filtrar ruidos espurios."""
        lecturas = []
        for _ in range(self._muestras_us):
            try:
                d = self._ultrasonico.distance_cm()
                if d is not None and 2.0 <= d <= 400.0:
                    lecturas.append(d)
            except OSError:
                pass
            sleep_us(500)

        if not lecturas:
            return 400.0  # Retorno seguro si falla la lectura
        return sum(lecturas) / len(lecturas)

    def leer_ir_izquierdo(self):
        """Devuelve True si detecta un obstáculo cercano a la izquierda (Estado LOW)."""
        return self._ir_izq.value() == 0

    def leer_ir_derecho(self):
        """Devuelve True si detecta un obstáculo cercano a la derecha (Estado LOW)."""
        return self._ir_der.value() == 0

    def detectar_caida(self):
        """Calcula el módulo resultante para detectar impactos escalados a Fuerzas G."""
        if not self._mpu_ok:
            return False
        try:
            ax, ay, az = self._mpu.accel.xyz
            # Módulo de aceleración resultante en m/s^2
            a_total_ms2 = (ax**2 + ay**2 + az**2) ** 0.5
            # Convertimos m/s^2 a Gs dividiendo por la gravedad normal de la Tierra (9.80665)
            a_total_g = a_total_ms2 / 9.80665
            return a_total_g > self._umbral_caida
        except Exception as e:
            print("[SensorBox] Error MPU6050 en lectura:", e)
            return False

    def obtener_resumen_global(self):
        """Empaqueta la telemetría en un solo diccionario listo para MQTT."""
        try:
            temp = self._mpu.temperature if self._mpu_ok else 0.0
        except:
            temp = 0.0

        return {
            "distancia_cm": self.leer_distancia_cm(),
            "ir_izq"      : self.leer_ir_izquierdo(),
            "ir_der"      : self.leer_ir_derecho(),
            "caida"       : self.detectar_caida(),
            "temperatura" : temp
        }


# ─────────────────────────────────────────────────────────────────────────────
# CLASE: ActuatorBox (Gestor de salidas físicas y alertas de usuario)
# ─────────────────────────────────────────────────────────────────────────────
class ActuatorBox:
    """
    Abstrae el conjunto de actuadores del sistema Safe-Path:
    Reproductor de voz DFPlayer Mini, Motor Vibrador Háptico y Buzzer de Proximidad.
    """

    # Códigos hexadecimales del protocolo del DFPlayer Mini
    _DF_START   = 0x7E
    _DF_VERSION = 0xFF
    _DF_LEN     = 0x06
    _DF_END     = 0xEF
    _DF_CMD_PLY = 0x03  # Comando universal de reproducción de pista (Specify Track)
    _DF_CMD_VOL = 0x06
    _DF_CMD_STP = 0x16

    # Constantes lógicas de las pistas de la tarjeta MicroSD
    PISTA_OBSTACULO_FRONTAL = 1
    PISTA_OBSTACULO_IZQ     = 2
    PISTA_OBSTACULO_DER     = 3
    PISTA_CAIDA_DETECTADA   = 4
    PISTA_DESCONOCIDO       = 9

    # Umbral de distancia crítico para activación física del buzzer (en cm)
    UMBRAL_BUZZER_CRITICO_CM = 30.0

    def __init__(self, 
                 pin_dfplayer_tx=26, pin_dfplayer_rx=25, 
                 pin_motor=33, pin_buzzer=2, 
                 volumen=20):
        
        # 1. Configuración del DFPlayer Mini (MIGRADO A UART1 PARA EVITAR CONFLICTO CON GPS)
        try:
            from machine import UART
            # Inicializamos UART1 por hardware (TX=26, RX=25) para dejar libre UART2 al GPS
            self._uart = UART(1, baudrate=9600, tx=Pin(pin_dfplayer_tx), rx=Pin(pin_dfplayer_rx))
            self._df_disponible = True
            time.sleep(0.5)
            self._set_volumen(volumen)
            print("[ActuatorBox] DFPlayer Mini inicializado en UART1 con éxito.")
        except Exception as e:
            print("[ActuatorBox] Error crítico al inicializar el DFPlayer:", e)
            self._df_disponible = False

        # 2. Configuración del Motor Vibrador (Alerta Háptica en GPIO 33)
        self._motor = Pin(pin_motor, Pin.OUT)
        self._motor.off()

        # 3. Configuración del Buzzer Activo (Alerta Acústica en GPIO 2)
        self._buzzer = Pin(pin_buzzer, Pin.OUT)
        self._buzzer.off()

        print("[ActuatorBox] Inicializado con soporte de alertas de voz, motor háptico y buzzer.")

    # ─────────────────────────────────────────────────────────────────────────
    # Métodos del DFPlayer Mini (Audio de Voz)
    # ─────────────────────────────────────────────────────────────────────────
    def _enviar_trama(self, cmd, param_hi=0x00, param_lo=0x00):
        if not self._df_disponible:
            return
        
        # Suma de bytes para el cálculo de redundancia cíclica estándar
        suma_bytes = self._DF_VERSION + self._DF_LEN + cmd + 0x00 + param_hi + param_lo
        # Cálculo del checksum con máscara estricta de 16 bits sin signo
        checksum = (0x10000 - suma_bytes) & 0xFFFF
        chk_hi = (checksum >> 8) & 0xFF
        chk_lo = checksum & 0xFF
        
        paquete = bytes([
            self._DF_START, self._DF_VERSION, self._DF_LEN,
            cmd, 0x00, param_hi, param_lo,
            chk_hi, chk_lo, self._DF_END
        ])
        self._uart.write(paquete)

    def _set_volumen(self, nivel):
        nivel = max(0, min(30, nivel))
        self._enviar_trama(self._DF_CMD_VOL, 0x00, nivel)

    def reproducir_audio(self, num_pista):
        """Manda la trama serial dividida en bytes para reproducir la pista seleccionada."""
        if self._df_disponible:
            # Separación matemática del número de pista en Byte Alto y Byte Bajo (16 bits)
            param_hi = (num_pista >> 8) & 0xFF
            param_lo = num_pista & 0xFF
            self._enviar_trama(self._DF_CMD_PLY, param_hi, param_lo)
        else:
            print(f"[ActuatorBox] Bocina Virtual: Reproduciendo pista #{num_pista}")

    # ─────────────────────────────────────────────────────────────────────────
    # Métodos del Motor Vibrador (Alerta Háptica)
    # ─────────────────────────────────────────────────────────────────────────
    def activar_alerta_haptica(self):
        """Enciende el motor de vibración para advertir proximidad media o caídas."""
        self._motor.on()

    def desactivar_alerta_haptica(self):
        """Apaga el motor de vibración."""
        self._motor.off()

    # ─────────────────────────────────────────────────────────────────────────
    # Métodos del Buzzer Activo (Alerta Acústica vinculada a la distancia)
    # ─────────────────────────────────────────────────────────────────────────
    def encender_buzzer(self):
        """Activa de forma continua el buzzer activo."""
        self._buzzer.on()

    def apagar_buzzer(self):
        """Desactiva el buzzer activo."""
        self._buzzer.off()

    def actualizar_alerta_distancia(self, distancia_cm):
        """
        Lógica de alarma basada estrictamente en la distancia del ultrasónico.
        Si el obstáculo está a menos de 30 cm (riesgo de choque inminente),
        el buzzer se enciende para alertar sonoramente al usuario.
        """
        if distancia_cm <= self.UMBRAL_BUZZER_CRITICO_CM:
            self.encender_buzzer()
        else:
            self.apagar_buzzer()

    # ─────────────────────────────────────────────────────────────────────────
    # Método de Estado Seguro (ESTADO SEGURO - Apagado total)
    # ─────────────────────────────────────────────────────────────────────────
    def silenciar_todo(self):
        """
        ESTADO SEGURO: Apaga instantáneamente el motor de vibración, 
        el buzzer y detiene la reproducción del DFPlayer Mini.
        """
        # 1. Silenciar DFPlayer
        if self._df_disponible:
            self._enviar_trama(self._DF_CMD_STP)
        
        # 2. Desactivar salidas físicas de potencia
        self.desactivar_alerta_haptica()
        self.apagar_buzzer()
        
        print("[ActuatorBox] [ESTADO SEGURO ACTIVADO] Todos los actuadores apagados.")


# ─────────────────────────────────────────────────────────────────────────────
# CLASE: MQTTManager (Mantenida intacta para transmisión de telemetría)
# ─────────────────────────────────────────────────────────────────────────────
class MQTTManager:
    def __init__(self, broker, puerto=1883, usuario="", contrasena="", client_id="safepath_client"):
        self._broker     = broker
        self._puerto     = puerto
        self._usuario    = usuario
        self._contrasena = contrasena
        self._client_id  = client_id
        self._cliente    = None
        self._conectado  = False
        self._callbacks  = {}

    def registrar_callback(self, topico, funcion):
        self._callbacks[topico] = funcion

    def conectar(self):
        try:
            from umqtt.simple import MQTTClient
            
            # LÓGICA DE DETECCIÓN DE SSL: Si el puerto es 8883 (HiveMQ Cloud), activamos el cifrado SSL/TLS obligatorio
            utilizar_ssl = (self._puerto == 8883)
            config_ssl = {}
            
            if utilizar_ssl:
                # El parámetro "server_hostname" es indispensable para verificar certificados.
                # Al pasar un diccionario vacío, le decimos a MicroPython que use SSL en modo '--insecure',
                # permitiendo la conexión cifrada sin verificar las claves criptográficas locales.
                config_ssl = {"server_hostname": self._broker}
            
            self._cliente = MQTTClient(
                self._client_id, self._broker,
                user=self._usuario, password=self._contrasena,
                port=self._puerto,
                ssl=utilizar_ssl,
                ssl_params=config_ssl
            )
            self._cliente.set_callback(self._dispatcher)
            self._cliente.connect()
            for topico in self._callbacks:
                self._cliente.subscribe(topico.encode())
            self._conectado = True
            print(f"[MQTTManager] Conexión SSL exitosa con HiveMQ: {self._broker}")
            return True
        except Exception as e:
            print("[MQTTManager] Fallo de conexión:", e)
            self._conectado = False
            return False

    def _dispatcher(self, topico_bytes, msg_bytes):
        topico = topico_bytes.decode()
        mensaje = msg_bytes.decode()
        if topico in self._callbacks:
            try:
                self._callbacks[topico](topico, mensaje)
            except Exception as e:
                print(f"[MQTTManager] Error en callback '{topico}':", e)

    def publicar(self, topico, mensaje):
        if not self._conectado:
            self.conectar()
        try:
            self._cliente.publish(topico.encode(), mensaje.encode())
            return True
        except Exception as e:
            print("[MQTTManager] Error de publicación:", e)
            self._conectado = False
            return False

    def verificar_mensajes(self):
        if self._conectado:
            try:
                self._cliente.check_msg()
            except Exception as e:
                print("[MQTTManager] Error de lectura de mensajes:", e)
                self._conectado = False

    @property
    def conectado(self):
        return self._conectado


# ─────────────────────────────────────────────────────────────────────────────
# CLASE: FirebaseClient (Mantenida intacta para subida histórica)
# ─────────────────────────────────────────────────────────────────────────────
class FirebaseClient:
    def __init__(self, api_key, project_id, coleccion):
        self._api_key    = api_key
        self._project_id = project_id
        self._coleccion  = coleccion
        self._url = (
            f"https://firestore.googleapis.com/v1/projects/{project_id}"
            f"/databases/(default)/documents/{coleccion}?key={api_key}"
        )

    def enviar_evento(self, datos_dict):
        import urequests
        import json

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
            print("[FirebaseClient] Error al escribir en la nube:", e)
            return False
