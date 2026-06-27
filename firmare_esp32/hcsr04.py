# =============================================================================
# PROYECTO   : Safe-Path AI
# ARCHIVO    : hcsr04.py
# DESCRIPCIÓN: Driver optimizado en MicroPython para el sensor ultrasónico HC-SR04.
#              Mide el tiempo de retorno del pulso sónico para calcular distancias.
# =============================================================================

import machine
import time

class HCSR04:
    def __init__(self, trigger_pin, echo_pin, echo_timeout_us=500*2*30):
        """
        Inicializa el transductor ultrasónico.
        Ajusta un timeout por defecto para evitar congelar el procesador
        si la onda de sonido no rebota.
        """
        self.echo_timeout_us = echo_timeout_us
        self.trigger = machine.Pin(trigger_pin, mode=machine.Pin.OUT)
        self.trigger.value(0)
        self.echo = machine.Pin(echo_pin, mode=machine.Pin.IN)

    def _send_pulse_and_return_time(self):
        """Envia un pulso ultrasónico de 10us y mide el tiempo de respuesta."""
        self.trigger.value(0)
        time.sleep_us(5)
        self.trigger.value(1)
        time.sleep_us(10)
        self.trigger.value(0)
        try:
            # Mide la duración del pulso en alto (1) en microsegundos
            pulse_time = machine.time_pulse_us(self.echo, 1, self.echo_timeout_us)
            return pulse_time
        except OSError as ex:
            if ex.args[0] == 110: # ETIMEDOUT
                return -1
            raise ex

    def distance_mm(self):
        """Devuelve la distancia medida en milímetros."""
        pulse_time = self._send_pulse_and_return_time()
        if pulse_time < 0:
            return None
        # La velocidad del sonido es 340 m/s (0.34 mm/us)
        # Distancia = (tiempo * 0.34) / 2
        return pulse_time * 0.17182

    def distance_cm(self):
        """Devuelve la distancia medida en centímetros."""
        pulse_time = self._send_pulse_and_return_time()
        if pulse_time < 0:
            return None
        # Distancia = (tiempo * 0.0343) / 2
        return (pulse_time / 2) / 29.1