# =============================================================================
# PROYECTO   : Safe-Path AI
# ARCHIVO    : imu.py
# DESCRIPCIÓN: Driver en MicroPython para el giroscopio y acelerómetro MPU6050.
#              Lee los registros I2C de aceleración y temperatura interna.
# =============================================================================

from machine import Pin
from vector3d import Vector3d
import time

class MPU6050:
    def __init__(self, i2c, address=0x68):
        self.i2c = i2c
        self.address = address
        
        # Despertar el MPU6050 (por defecto arranca en modo sleep)
        try:
            self.i2c.writeto_mem(self.address, 0x6B, b'\x00')
            time.sleep_ms(50)
        except Exception as e:
            raise OSError("No se detectó el chip MPU6050 en el bus I2C.") from e
        
        # Inicialización de sub-módulos lógicos
        self.accel = Accel(self.i2c, self.address)
        self.gyro = Gyro(self.i2c, self.address)

    @property
    def temperature(self):
        """Devuelve la temperatura interna del chip en grados Celsius."""
        try:
            raw_temp = self._read_word(0x41)
            # Conversión matemática según la hoja de datos oficial
            return (raw_temp / 340.0) + 36.53
        except:
            return 0.0

    def _read_word(self, register):
        """Lee un entero con signo de 16 bits de los registros del chip."""
        buf = self.i2c.readfrom_mem(self.address, register, 2)
        value = (buf[0] << 8) | buf[1]
        if value > 32767:
            value -= 65536
        return value


class Accel:
    def __init__(self, i2c, address):
        self.i2c = i2c
        self.address = address

    def _read_word(self, register):
        buf = self.i2c.readfrom_mem(self.address, register, 2)
        value = (buf[0] << 8) | buf[1]
        if value > 32767:
            value -= 65536
        return value

    @property
    def xyz(self):
        """Devuelve la aceleración de los tres ejes en m/s^2 como una tupla (ax, ay, az)."""
        try:
            # Rango por defecto: +/- 2g (Sensibilidad de 16384 LSB/g)
            # Multiplicamos por 9.80665 para obtener m/s^2
            ax = self._read_word(0x3B) / 16384.0 * 9.80665
            ay = self._read_word(0x3D) / 16384.0 * 9.80665
            az = self._read_word(0x3F) / 16384.0 * 9.80665
            return ax, ay, az
        except:
            return 0.0, 0.0, 0.0


class Gyro:
    def __init__(self, i2c, address):
        self.i2c = i2c
        self.address = address

    def _read_word(self, register):
        buf = self.i2c.readfrom_mem(self.address, register, 2)
        value = (buf[0] << 8) | buf[1]
        if value > 32767:
            value -= 65536
        return value

    @property
    def xyz(self):
        """Devuelve la velocidad angular de los tres ejes en grados/segundo."""
        try:
            # Rango por defecto: +/- 250 deg/s (Sensibilidad de 131 LSB/deg/s)
            gx = self._read_word(0x43) / 131.0
            gy = self._read_word(0x45) / 131.0
            gz = self._read_word(0x47) / 131.0
            return gx, gy, gz
        except:
            return 0.0, 0.0, 0.0