from machine import Pin
import uasyncio as asyncio


class LedRGBManager:
    """
    Controlador del LED RGB de estado de la mochila Vision Guard.

    GPIO 5  -> Rojo
    GPIO 18 -> Verde
    GPIO 19 -> Azul
    """

    def __init__(self):

        self.rojo = Pin(5, Pin.OUT)
        self.verde = Pin(18, Pin.OUT)
        self.azul = Pin(19, Pin.OUT)

        self.apagar()

    # --------------------------------------------------------
    # Método privado
    # --------------------------------------------------------

    def _set_color(self, r=False, g=False, b=False):

        self.rojo.value(1 if r else 0)
        self.verde.value(1 if g else 0)
        self.azul.value(1 if b else 0)

    # --------------------------------------------------------
    # Estados del sistema
    # --------------------------------------------------------

    def apagar(self):
        self._set_color()

    def estado_vinculado(self):
        print("[LED] Estado: Vinculado")
        self._set_color(b=True)

    def estado_recorrido(self):
        print("[LED] Estado: Recorrido Activo")
        self._set_color(g=True)

    def estado_finalizado(self):
        print("[LED] Estado: Recorrido Finalizado")
        self._set_color(r=True)

    # --------------------------------------------------------
    # Parpadeos
    # --------------------------------------------------------

    async def parpadear_azul(self, veces=3):
        for _ in range(veces):
            self.estado_vinculado()
            await asyncio.sleep(0.3)
            self.apagar()
            await asyncio.sleep(0.3)
        self.estado_vinculado()


    async def parpadear_verde(self, veces=3):
        for _ in range(veces):
            self.estado_recorrido()
            await asyncio.sleep(0.3)
            self.apagar()
            await asyncio.sleep(0.3)
        self.estado_recorrido()


    async def parpadear_rojo(self, veces=3):
        for _ in range(veces):
            self.estado_finalizado()
            await asyncio.sleep(0.3)
            self.apagar()
            await asyncio.sleep(0.3)
        self.estado_finalizado()