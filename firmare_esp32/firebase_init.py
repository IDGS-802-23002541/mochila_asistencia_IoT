# =============================================================================
# PROYECTO   : Vision Guard
# ARCHIVO    : firebase_init.py
# DESCRIPCIÓN: Inicialización única de Firebase Admin SDK y exposición del
#              cliente Firestore para toda la aplicación.
# =============================================================================
import firebase_admin
from firebase_admin import credentials, firestore
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def initialize_firebase():
    """
    Inicializa Firebase Admin SDK usando la cuenta de servicio.
    Es seguro llamarla múltiples veces; solo inicializa una vez.

    Archivo requerido: credentials/serviceAccountKey.json
    (Descargar desde Firebase Console → Configuración del proyecto → Cuentas de servicio)
    """
    if not firebase_admin._apps:
        try:
            cred = credentials.Certificate('credentials/serviceAccountKey.json')
            firebase_admin.initialize_app(cred)
            logger.info("Firebase inicializado correctamente.")
        except FileNotFoundError:
            logger.error("No se encontró credentials/serviceAccountKey.json. "
                         "Descárgalo desde Firebase Console.")
            raise
        except Exception as e:
            logger.error(f"Error al inicializar Firebase: {e}")
            raise
    else:
        logger.info("Firebase ya estaba inicializado.")


# Inicializar al importar y exponer cliente global
initialize_firebase()
db = firestore.client()
