# =============================================================================
# PROYECTO   : Safe-Path AI
# ARCHIVO    : vector3d.py
# DESCRIPCIÓN: Clase de soporte matemático para representar vectores tridimensionales (x, y, z).
#              Indispensable para procesar las aceleraciones del giroscopio.
# =============================================================================

class Vector3d:
    def __init__(self, x=0, y=0, z=0):
        self.x = x
        self.y = y
        self.z = z

    def __repr__(self):
        return "Vector3d({:0.2f}, {:0.2f}, {:0.2f})".format(self.x, self.y, self.z)

    @property
    def xyz(self):
        """Devuelve las componentes del vector como una tupla (x, y, z)."""
        return self.x, self.y, self.z