# =============================================================================
# PROYECTO   : Safe-Path AI — Sistema de Navegación Aumentada
# ARCHIVO    : recognition.py
# DESCRIPCIÓN: Módulo de entrenamiento y reconocimiento:
#                - Reconocimiento FACIAL con face_recognition + dlib
#                - Reconocimiento de OBJETOS con ResNet50 (TensorFlow/Keras)
#                - Detección en tiempo real con SSD MobileNet (OpenCV DNN)
#              RECICLADO DE: SmartCap/Servidor/recognition.py y
#              SistemasProgramables/recognition.py (idénticos).
#              MEJORAS RESPECTO AL ORIGINAL:
#                - Clases FaceRecognizer y ObjectRecognizer encapsuladas
#                - Recarga en caliente del modelo facial sin reiniciar el servidor
#                - Umbral de distancia facial configurable (antes fijo)
#                - Logging unificado con el servidor principal
#                - Sanitización reutilizable en funciones independientes
# =============================================================================

import os
import shutil
import logging
import pickle
from datetime import datetime
from typing import List, Optional, Tuple

import cv2
import numpy as np
import face_recognition
import tensorflow as tf
from tensorflow.keras.applications.resnet50 import ResNet50, preprocess_input
from tensorflow.keras.preprocessing import image as keras_image
from tensorflow.keras.models import Model

from fastapi import HTTPException
from firebase_init import db

# ─── Logging ─────────────────────────────────────────────────────────────────
logger = logging.getLogger(__name__)

# ─── Rutas de directorios ─────────────────────────────────────────────────────
PATTERNS_DIR   = 'patterns'
FACES_DIR      = os.path.join(PATTERNS_DIR, 'faces')
OBJECTS_DIR    = os.path.join(PATTERNS_DIR, 'objects')
FACE_MODEL_PKL = os.path.join(PATTERNS_DIR, 'face_encodings.pkl')
OBJ_MODEL_PKL  = os.path.join(PATTERNS_DIR, 'object_encodings.pkl')

# Modelo SSD MobileNet para detección en tiempo real (carrito)
COCO_NAMES   = os.path.join(PATTERNS_DIR, 'coco.names')
SSD_CONFIG   = os.path.join(PATTERNS_DIR, 'ssd_mobilenet_v3_large_coco_2020_01_14.pbtxt')
SSD_WEIGHTS  = os.path.join(PATTERNS_DIR, 'frozen_inference_graph.pb')

os.makedirs(FACES_DIR,   exist_ok=True)
os.makedirs(OBJECTS_DIR, exist_ok=True)


# ─────────────────────────────────────────────────────────────────────────────
# FUNCIONES AUXILIARES DE SANITIZACIÓN
# Recicladas de recognition.py original; extraídas como funciones libres
# para poder usarlas desde add_user.py y app.py sin duplicar código.
# ─────────────────────────────────────────────────────────────────────────────
def sanitizar_nombre_archivo(nombre: str) -> str:
    """Elimina caracteres peligrosos de un nombre de archivo."""
    return "".join(c for c in nombre if c.isalnum() or c in (' ', '_', '-')).rstrip()


def sanitizar_nombre(nombre: str) -> str:
    """Elimina caracteres peligrosos de un nombre de usuario o carpeta."""
    return "".join(c for c in nombre if c.isalnum() or c in (' ', '_', '-')).rstrip()


# ─────────────────────────────────────────────────────────────────────────────
# CLASE: FaceRecognizer
# Encapsula el modelo facial (face_recognition + dlib).
# Permite recarga en caliente sin reiniciar el servidor.
# ─────────────────────────────────────────────────────────────────────────────
class FaceRecognizer:
    """
    Gestor del modelo de reconocimiento facial.

    Uso:
        reconocedor = FaceRecognizer()
        nombre = reconocedor.identificar(encoding_de_la_imagen)
        reconocedor.recargar()   # después de entrenar
    """

    def __init__(self, umbral_distancia: float = 0.55):
        """
        Parámetro:
            umbral_distancia: distancia máxima para considerar una coincidencia.
            Valor original en SmartCap: comparación booleana (sin umbral explícito).
            Aquí se hace configurable. Valores más bajos = más estricto.
        """
        self._umbral = umbral_distancia
        self._encodings: List[np.ndarray] = []
        self._nombres:   List[str]        = []
        self._cargar_modelo()

    def _cargar_modelo(self):
        """Carga el modelo desde el archivo .pkl si existe."""
        if os.path.exists(FACE_MODEL_PKL):
            try:
                with open(FACE_MODEL_PKL, 'rb') as f:
                    data = pickle.load(f)
                self._encodings = data.get('encodings', [])
                self._nombres   = data.get('names',     [])
                logger.info(f"[FaceRecognizer] Modelo cargado: {len(self._nombres)} personas.")
            except Exception as e:
                logger.error(f"[FaceRecognizer] Error al cargar modelo: {e}")
                self._encodings, self._nombres = [], []
        else:
            logger.warning("[FaceRecognizer] No existe face_encodings.pkl. Modelo vacío.")
            self._encodings, self._nombres = [], []

    def recargar(self):
        """Recarga el modelo en caliente (llamar después de entrenar)."""
        self._cargar_modelo()
        logger.info("[FaceRecognizer] Modelo recargado en caliente.")

    def identificar(self, encoding: np.ndarray) -> str:
        """
        Compara un encoding contra los conocidos y devuelve el nombre más cercano.
        Devuelve "Desconocido" si no hay coincidencia o el modelo está vacío.

        LÓGICA RECICLADA de handle_image_gorra() en app.py del SmartCap,
        extraída aquí para separar IA de la capa HTTP.
        """
        if not self._encodings:
            return "Desconocido"

        distancias = face_recognition.face_distance(self._encodings, encoding)
        idx_mejor  = int(np.argmin(distancias))

        if distancias[idx_mejor] <= self._umbral:
            return self._nombres[idx_mejor]
        return "Desconocido"

    def procesar_frame(self, img_bgr: np.ndarray) -> Tuple[np.ndarray, List[str]]:
        """
        Detecta y reconoce rostros en un frame BGR de OpenCV.
        Dibuja bounding boxes y nombres.

        Devuelve: (imagen_anotada, lista_de_nombres)

        RECICLADO de handle_image_gorra() del SmartCap.
        """
        rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
        ubicaciones  = face_recognition.face_locations(rgb)
        encodings_fr = face_recognition.face_encodings(rgb, ubicaciones)

        nombres = []
        for enc in encodings_fr:
            nombre = self.identificar(enc)
            nombres.append(nombre)

        # Dibujar resultados
        for (top, right, bottom, left), nombre in zip(ubicaciones, nombres):
            cv2.rectangle(img_bgr, (left, top), (right, bottom), (0, 255, 0), 2)
            cv2.putText(img_bgr, nombre, (left, top - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

        return img_bgr, nombres

    @property
    def modelo_vacio(self) -> bool:
        return len(self._encodings) == 0


# ─────────────────────────────────────────────────────────────────────────────
# CLASE: ObjectDetector (SSD MobileNet — detección en tiempo real)
# Para el carrito: detecta personas, autos, señales de tránsito, fuego, etc.
# ─────────────────────────────────────────────────────────────────────────────
class ObjectDetector:
    """
    Detector de objetos en tiempo real usando SSD MobileNet (COCO).

    RECICLADO de handle_image_carro() y la inicialización del net en app.py.
    Encapsulado en clase para facilitar el reemplazo por YOLOv8 en el futuro.
    """

    def __init__(self, umbral_confianza: float = 0.5):
        self._umbral = umbral_confianza
        self._nombres_clases: List[str] = []
        self._red = None
        self._cargar_modelo()

    def _cargar_modelo(self):
        """Carga los pesos SSD MobileNet y las etiquetas COCO."""
        try:
            with open(COCO_NAMES, 'rt') as f:
                self._nombres_clases = f.read().rstrip('\n').split('\n')

            self._red = cv2.dnn_DetectionModel(SSD_WEIGHTS, SSD_CONFIG)
            self._red.setInputSize(320, 320)
            self._red.setInputScale(1.0 / 127.5)
            self._red.setInputMean((127.5, 127.5, 127.5))
            self._red.setInputSwapRB(True)
            logger.info(f"[ObjectDetector] SSD MobileNet cargado "
                        f"({len(self._nombres_clases)} clases COCO).")
        except FileNotFoundError as e:
            logger.warning(f"[ObjectDetector] Archivos del modelo no encontrados: {e}. "
                           "Copiar coco.names, ssd_mobilenet_v3_large_coco_2020_01_14.pbtxt "
                           "y frozen_inference_graph.pb a la carpeta patterns/.")
            self._red = None

    def procesar_frame(self, img_bgr: np.ndarray) -> Tuple[np.ndarray, List[str]]:
        """
        Detecta objetos en un frame BGR.
        Dibuja bounding boxes y etiquetas.

        Devuelve: (imagen_anotada, lista_de_etiquetas_detectadas)

        RECICLADO de handle_image_carro() del SmartCap.
        """
        if self._red is None:
            return img_bgr, []

        rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
        ids_clase, confs, bbox = self._red.detect(rgb, confThreshold=self._umbral)

        etiquetas_detectadas = []
        if len(ids_clase) > 0:
            for clase_id, conf, caja in zip(ids_clase.flatten(),
                                             confs.flatten(),
                                             bbox):
                etiqueta = str(self._nombres_clases[clase_id - 1])
                etiquetas_detectadas.append(etiqueta)
                cv2.rectangle(img_bgr,
                              (caja[0], caja[1]),
                              (caja[0] + caja[2], caja[1] + caja[3]),
                              (0, 255, 0), 2)
                cv2.putText(img_bgr, etiqueta, (caja[0], caja[1] - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

        return img_bgr, etiquetas_detectadas

    @property
    def disponible(self) -> bool:
        return self._red is not None


# ─────────────────────────────────────────────────────────────────────────────
# CLASE: ObjectFeatureRecognizer (ResNet50 — reconocimiento por características)
# Para el carrito: reconoce objetos específicos entrenados por el usuario.
# ─────────────────────────────────────────────────────────────────────────────
class ObjectFeatureRecognizer:
    """
    Reconocedor de objetos personalizado usando ResNet50 como extractor
    de características y comparación por distancia coseno.

    RECICLADO de extract_object_features() y entrenar_modelo_objetos()
    del recognition.py original.
    """

    def __init__(self):
        self._caracteristicas: List[np.ndarray] = []
        self._etiquetas:       List[str]        = []
        self._modelo = None
        self._inicializar_resnet()
        self._cargar_modelo()

    def _inicializar_resnet(self):
        """Carga ResNet50 preentrenado como extractor de características."""
        try:
            base = ResNet50(weights='imagenet', include_top=False, pooling='avg')
            self._modelo = Model(inputs=base.input, outputs=base.output)
            logger.info("[ObjectFeatureRecognizer] ResNet50 cargado.")
        except Exception as e:
            logger.error(f"[ObjectFeatureRecognizer] Error al cargar ResNet50: {e}")
            self._modelo = None

    def _cargar_modelo(self):
        """Carga el modelo entrenado desde object_encodings.pkl."""
        if os.path.exists(OBJ_MODEL_PKL):
            try:
                with open(OBJ_MODEL_PKL, 'rb') as f:
                    data = pickle.load(f)
                self._caracteristicas = data.get('features', [])
                self._etiquetas       = data.get('labels',   [])
                logger.info(f"[ObjectFeatureRecognizer] {len(self._etiquetas)} "
                            "objetos entrenados cargados.")
            except Exception as e:
                logger.error(f"[ObjectFeatureRecognizer] Error al cargar modelo: {e}")

    def recargar(self):
        """Recarga el modelo en caliente."""
        self._cargar_modelo()

    def extraer_caracteristicas(self, ruta_imagen: str) -> Optional[np.ndarray]:
        """
        Extrae vector de características de una imagen usando ResNet50.
        RECICLADO de extract_object_features() del original.
        """
        if self._modelo is None:
            return None
        try:
            img       = keras_image.load_img(ruta_imagen, target_size=(224, 224))
            arr       = keras_image.img_to_array(img)
            arr       = np.expand_dims(arr, axis=0)
            arr       = preprocess_input(arr)
            features  = self._modelo.predict(arr, verbose=0)
            return features.flatten()
        except Exception as e:
            logger.error(f"[ObjectFeatureRecognizer] Error al extraer features de "
                         f"{ruta_imagen}: {e}")
            return None

    def identificar(self, caracteristicas: np.ndarray, umbral: float = 0.8) -> str:
        """
        Compara un vector de características contra los entrenados.
        Usa distancia L2 normalizada (similar a coseno).
        """
        if not self._caracteristicas:
            return "Desconocido"

        distancias = [
            np.linalg.norm(caracteristicas - c)
            for c in self._caracteristicas
        ]
        idx_mejor = int(np.argmin(distancias))
        if distancias[idx_mejor] < umbral:
            return self._etiquetas[idx_mejor]
        return "Desconocido"


# ─────────────────────────────────────────────────────────────────────────────
# FUNCIONES DE ENTRENAMIENTO (mantienen la misma firma del original para
# compatibilidad con gestionar_modelo_facial() y gestionar_modelo_objetos()
# de app.py)
# ─────────────────────────────────────────────────────────────────────────────
def entrenar_modelo_facial(reconocedor: Optional[FaceRecognizer] = None):
    """
    Entrena el modelo facial con todas las imágenes en patterns/faces/.
    Si se proporciona una instancia FaceRecognizer, la recarga en caliente.

    RECICLADO de recognition.py del SmartCap, refactorizado para:
      - Usar la clase FaceRecognizer para la recarga en caliente.
      - Mejor manejo de errores con conteo de imágenes procesadas.

    Lanza HTTPException si no se encuentran rostros (compatible con
    el endpoint /create_face_pattern de recognition.py original).
    """
    modelo_pkl = FACE_MODEL_PKL

    # Eliminar modelo anterior
    if os.path.exists(modelo_pkl):
        try:
            os.remove(modelo_pkl)
            logger.info(f"[entrenamiento] Modelo facial anterior eliminado.")
        except Exception as e:
            logger.error(f"[entrenamiento] No se pudo eliminar modelo anterior: {e}")
            raise HTTPException(status_code=500,
                                detail="Error al eliminar el modelo existente.")

    encodings_conocidos: List[np.ndarray] = []
    nombres_conocidos:   List[str]        = []
    imagenes_procesadas = 0

    for nombre_usuario in os.listdir(FACES_DIR):
        dir_usuario = os.path.join(FACES_DIR, nombre_usuario)
        if not os.path.isdir(dir_usuario):
            continue
        for archivo in os.listdir(dir_usuario):
            ruta = os.path.join(dir_usuario, archivo)
            try:
                img  = face_recognition.load_image_file(ruta)
                encs = face_recognition.face_encodings(img)
                if encs:
                    encodings_conocidos.append(encs[0])
                    nombres_conocidos.append(nombre_usuario)
                    imagenes_procesadas += 1
                else:
                    logger.warning(f"Sin rostros en: {ruta}")
            except Exception as e:
                logger.error(f"Error procesando {ruta}: {e}")

    if not encodings_conocidos:
        raise HTTPException(status_code=400,
                            detail="No se encontraron rostros en las imágenes.")

    with open(modelo_pkl, 'wb') as f:
        pickle.dump({'encodings': encodings_conocidos, 'names': nombres_conocidos}, f)

    logger.info(f"[entrenamiento] Modelo facial guardado. "
                f"{len(nombres_conocidos)} encodings de "
                f"{len(set(nombres_conocidos))} personas.")

    # Recargar instancia en caliente si se proporcionó
    if reconocedor is not None:
        reconocedor.recargar()


def entrenar_modelo_objetos(reconocedor_obj: Optional[ObjectFeatureRecognizer] = None):
    """
    Entrena el modelo de objetos con todas las imágenes en patterns/objects/.
    RECICLADO de recognition.py del SmartCap, con recarga en caliente opcional.
    """
    modelo_pkl = OBJ_MODEL_PKL
    extractor  = ObjectFeatureRecognizer()  # instancia temporal para extraer features

    if os.path.exists(modelo_pkl):
        try:
            os.remove(modelo_pkl)
        except Exception as e:
            raise HTTPException(status_code=500,
                                detail=f"Error al eliminar modelo: {e}")

    features: List[np.ndarray] = []
    etiquetas: List[str]       = []

    for nombre_objeto in os.listdir(OBJECTS_DIR):
        dir_objeto = os.path.join(OBJECTS_DIR, nombre_objeto)
        if not os.path.isdir(dir_objeto):
            continue
        for archivo in os.listdir(dir_objeto):
            if not archivo.lower().endswith(('.png', '.jpg', '.jpeg')):
                continue
            ruta = os.path.join(dir_objeto, archivo)
            feat = extractor.extraer_caracteristicas(ruta)
            if feat is not None:
                features.append(feat)
                etiquetas.append(nombre_objeto)

    if not features:
        raise HTTPException(status_code=400,
                            detail="No se pudieron extraer características.")

    with open(modelo_pkl, 'wb') as f:
        pickle.dump({'features': features, 'labels': etiquetas}, f)

    logger.info(f"[entrenamiento] Modelo de objetos guardado. "
                f"{len(etiquetas)} imágenes de {len(set(etiquetas))} objetos.")

    if reconocedor_obj is not None:
        reconocedor_obj.recargar()


# ─────────────────────────────────────────────────────────────────────────────
# FUNCIÓN: guardar_patron_en_firebase
# Reciclada del endpoint /create_face_pattern del recognition.py original,
# extraída como función libre para reusar desde app.py.
# ─────────────────────────────────────────────────────────────────────────────
def guardar_patron_en_firebase(nombre: str, tipo: str,
                                dir_usuario: str, num_imagenes: int):
    """
    Registra un patrón de reconocimiento en la colección 'recognition_patterns'
    de Firestore.

    Parámetros:
        nombre       : nombre del usuario u objeto
        tipo         : 'persona' o 'objeto'
        dir_usuario  : ruta local donde se almacenan las imágenes
        num_imagenes : cantidad de imágenes guardadas
    """
    try:
        datos = {
            'name'          : nombre,
            'type'          : tipo.lower(),
            'directory_path': dir_usuario,
            'created_at'    : datetime.utcnow(),
            'image_count'   : num_imagenes,
        }
        db.collection('recognition_patterns').add(datos)
        logger.info(f"[Firebase] Patrón '{nombre}' ({tipo}) registrado con "
                    f"{num_imagenes} imágenes.")
    except Exception as e:
        logger.error(f"[Firebase] Error al registrar patrón: {e}")
        raise HTTPException(status_code=500,
                            detail="Error al registrar el patrón en Firebase.")


# ─────────────────────────────────────────────────────────────────────────────
# Instancias globales — importadas por app.py
# ─────────────────────────────────────────────────────────────────────────────
reconocedor_facial  = FaceRecognizer()
detector_objetos    = ObjectDetector()
reconocedor_objetos = ObjectFeatureRecognizer()
