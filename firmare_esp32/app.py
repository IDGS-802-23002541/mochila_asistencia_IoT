# =============================================================================
# PROYECTO   : Safe-Path AI — Sistema de Navegación Aumentada
# ARCHIVO    : app.py  (Servidor Python — E3/E4)
# DESCRIPCIÓN: Servidor FastAPI + SocketIO que integra:
#                - Autenticación JWT con cookies (reciclado SmartCap)
#                - MQTT bidireccional: carrito, gorra/mochila, GPS, Safe-Path
#                - Streaming de video: reconocimiento FACIAL (gorra/mochila)
#                  y detección de OBJETOS SSD MobileNet (carrito)
#                - Firebase Firestore: sensor_data, cap_sensors, gps_data,
#                  safepath_events, recognition_patterns
#                - Gestión de patrones de reconocimiento (CRUD + reentrenamiento)
#                - Dashboard GPS en tiempo real vía SocketIO
#                - Historial de sensores del carrito y mochila
#
#              RECICLADO DE:
#                - SmartCap/Servidor/app.py    (base completa)
#                - SistemasProgramables/app.py (carrito: motor, GPS, línea, fuego)
#              MEJORAS:
#                - Tópicos MQTT separados por dispositivo
#                - Clases FaceRecognizer/ObjectDetector desde recognition.py
#                - Endpoint /upload_frame_mochila (Safe-Path) además de /gorra
#                - Endpoint /safepath_event para recibir alertas de la mochila
#                - Endpoint /gps_data para recibir coordenadas del carrito
#                - Clase Historial extendida con GPS y eventos Safe-Path
#                - add_user.py reutilizable como script independiente
# =============================================================================

import os
import time
import json
import logging
import asyncio
import shutil
import glob
import pickle
from typing import Optional, List
from datetime import datetime, timedelta
from io import BytesIO

import cv2
import numpy as np
import face_recognition

from fastapi import (FastAPI, Depends, HTTPException, status,
                     Request, Form, BackgroundTasks, Response)
from fastapi.responses import (HTMLResponse, RedirectResponse,
                               JSONResponse, StreamingResponse)
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.exceptions import RequestValidationError

from jose import JWTError, jwt
from passlib.context import CryptContext

import firebase_admin
from firebase_admin import credentials, firestore
from firebase_init import db

import socketio
import paho.mqtt.client as mqtt

# Importar IA desde recognition.py
from recognition import (
    reconocedor_facial, detector_objetos, reconocedor_objetos,
    entrenar_modelo_facial, entrenar_modelo_objetos,
    guardar_patron_en_firebase, sanitizar_nombre, sanitizar_nombre_archivo,
    PATTERNS_DIR, FACES_DIR, OBJECTS_DIR
)

# ─────────────────────────────────────────────────────────────────────────────
# LOGGING
# ─────────────────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s %(levelname)s [%(name)s] %(message)s',
    handlers=[
        logging.FileHandler("server.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────────────────────────────────────
# FASTAPI + SOCKETIO
# ─────────────────────────────────────────────────────────────────────────────
sio          = socketio.AsyncServer(cors_allowed_origins="*")
fastapi_app  = FastAPI(title="Safe-Path AI Server", version="1.0")
socketio_app = socketio.ASGIApp(sio, fastapi_app)
app          = socketio_app   # ASGI para uvicorn/systemd

# ─────────────────────────────────────────────────────────────────────────────
# SEGURIDAD Y AUTENTICACIÓN (reciclado idéntico de SmartCap)
# ─────────────────────────────────────────────────────────────────────────────
SECRET_KEY                  = "safepath_clave_secreta_2025"
ALGORITHM                   = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class User:
    def __init__(self, id: str, username: str, hashed_password: str):
        self.id              = id
        self.username        = username
        self.hashed_password = hashed_password


def get_user(username: str) -> Optional[User]:
    try:
        docs = db.collection('users').where('username', '==', username).stream()
        for doc in docs:
            d = doc.to_dict()
            return User(id=doc.id,
                        username=d['username'],
                        hashed_password=d['password_hash'])
    except Exception as e:
        logger.error(f"Error al obtener usuario: {e}")
    return None


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def authenticate_user(username: str, password: str) -> Optional[User]:
    user = get_user(username)
    if user and verify_password(password, user.hashed_password):
        return user
    return None


def create_access_token(data: dict,
                        expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


async def get_current_user(request: Request) -> User:
    token = request.cookies.get("access_token", "")
    if token.startswith("Bearer "):
        token = token[7:]
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Token no proporcionado")
    try:
        payload  = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if not username:
            raise HTTPException(status_code=401, detail="Token inválido")
    except JWTError:
        raise HTTPException(status_code=401, detail="Token inválido")
    user = get_user(username)
    if not user:
        raise HTTPException(status_code=401, detail="Usuario no encontrado")
    return user


# ─────────────────────────────────────────────────────────────────────────────
# MIDDLEWARE Y ARCHIVOS ESTÁTICOS
# ─────────────────────────────────────────────────────────────────────────────
fastapi_app.add_middleware(CORSMiddleware,
                            allow_origins=["*"],
                            allow_credentials=True,
                            allow_methods=["*"],
                            allow_headers=["*"])

fastapi_app.mount("/static",   StaticFiles(directory="static"),   name="static")
fastapi_app.mount("/patterns", StaticFiles(directory="patterns"), name="patterns")
templates = Jinja2Templates(directory="templates")

# ─────────────────────────────────────────────────────────────────────────────
# CONFIGURACIÓN MQTT
# Tópicos reciclados del SmartCap + nuevos para Safe-Path AI
# ─────────────────────────────────────────────────────────────────────────────
MQTT_BROKER    = '34.30.116.129'
MQTT_PORT      = 1883
MQTT_USER      = 'aldo6868'
MQTT_PASSWORD  = 'Tapia5307='
MQTT_CLIENT_ID = 'safepath_server'

# ── Tópicos del CARRITO (reciclados de SistemasProgramables) ────────────────
T_CAR_CMDS      = 'car/commands'
T_CAR_POWER     = 'car/set_power'
T_CAR_SENSORES  = 'car/sensor_data'
T_CAR_GORRA     = 'car/gorra_commands'
T_CAR_FLASH     = 'flash'
T_CAR_CAP       = 'car/cap_sensors'

# ── Tópicos de la GORRA SmartCap (reciclados) ────────────────────────────────
T_GORRA_ROSTROS = 'cap/faces'

# ── Tópicos nuevos SAFE-PATH AI ───────────────────────────────────────────────
T_SP_SENSORES   = 'safepath/sensores'    # telemetría mochila → servidor
T_SP_ALERTAS    = 'safepath/alertas'     # alertas críticas mochila → servidor
T_SP_CMDS       = 'safepath/comandos'    # servidor → mochila
T_SP_RECONOCIDO = 'safepath/reconocido'  # servidor → mochila (nombre persona)
T_SP_GPS        = 'safepath/gps'         # mochila → servidor (posición GPS)

# ── Tópicos del GPS CARRITO ───────────────────────────────────────────────────
T_CAR_GPS       = 'car/gps'

mqtt_client = mqtt.Client(MQTT_CLIENT_ID)
mqtt_client.username_pw_set(MQTT_USER, MQTT_PASSWORD)


def _publicar(topic: str, mensaje: str):
    """Publica en MQTT si hay conexión; registra warning si no."""
    if mqtt_client.is_connected():
        mqtt_client.publish(topic, mensaje)
        logger.debug(f"[MQTT→] {topic}: {mensaje}")
    else:
        logger.warning(f"[MQTT] Sin conexión, no se publicó en {topic}")


def on_connect(client, userdata, flags, rc):
    if rc == 0:
        logger.info("[MQTT] Conectado al broker.")
        for t in [T_CAR_CMDS, T_CAR_POWER, T_CAR_SENSORES,
                  T_CAR_GORRA, T_CAR_FLASH, T_CAR_CAP,
                  T_GORRA_ROSTROS,
                  T_SP_SENSORES, T_SP_ALERTAS, T_SP_GPS, T_SP_CMDS,
                  T_CAR_GPS]:
            client.subscribe(t)
            logger.debug(f"[MQTT] Suscrito a: {t}")
    else:
        logger.error(f"[MQTT] Error al conectar, rc={rc}")


def on_message(client, userdata, msg):
    """
    Dispatcher de mensajes MQTT entrantes.
    RECICLADO de on_message() del SmartCap, extendido con tópicos Safe-Path.
    """
    try:
        topico  = msg.topic
        payload = msg.payload.decode() if isinstance(msg.payload, bytes) else msg.payload
        logger.info(f"[MQTT←] {topico}: {payload}")

        if topico in [T_CAR_CMDS, T_CAR_POWER]:
            sio.start_background_task(
                sio.emit, 'mqtt_command', {'topic': topico, 'command': payload})
        elif topico == T_CAR_SENSORES:
            procesar_datos_sensor(payload)
        elif topico == T_CAR_GORRA:
            sio.start_background_task(
                sio.emit, 'mqtt_command_gorra', {'topic': topico, 'command': payload})
        elif topico == T_CAR_FLASH:
            sio.start_background_task(
                sio.emit, 'mqtt_command_flash', {'topic': topico, 'command': payload})
        elif topico == T_CAR_CAP:
            procesar_cap_sensor(payload)
        elif topico == T_GORRA_ROSTROS:
            # Reenviar al dashboard en tiempo real
            sio.start_background_task(
                sio.emit, 'rostro_reconocido', {'nombre': payload})
        elif topico == T_SP_SENSORES:
            procesar_safepath_sensores(payload)
        elif topico == T_SP_ALERTAS:
            procesar_safepath_alerta(payload)
        elif topico in [T_SP_GPS, T_CAR_GPS]:
            procesar_gps(payload, fuente="mochila" if topico == T_SP_GPS else "carrito")
    except Exception as e:
        logger.error(f"[MQTT] Error en on_message: {e}")


mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message

try:
    mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)
    mqtt_client.loop_start()
    logger.info("[MQTT] Conexión iniciada.")
except Exception as e:
    logger.critical(f"[MQTT] Fallo al conectar: {e}")


# ─────────────────────────────────────────────────────────────────────────────
# CLASE: Historial (extendida de SmartCap)
# ─────────────────────────────────────────────────────────────────────────────
class Historial:
    """
    Acceso a las colecciones históricas de Firestore.
    RECICLADO de la clase Historial del SmartCap/app.py.
    NUEVO: obtener_gps_data() y obtener_safepath_events().
    """

    def __init__(self, db_client):
        self._db = db_client

    # ── Reciclado del SmartCap ────────────────────────────────────────────────
    def obtener_datos_sensor(self, limite=100) -> List[dict]:
        """Sensores del carrito (ultrasonido, IR, humo)."""
        try:
            docs = (self._db.collection('sensor_data')
                    .order_by('timestamp', direction=firestore.Query.DESCENDING)
                    .limit(limite).stream())
            resultado = []
            for doc in docs:
                s  = doc.to_dict()
                ts = s.get('timestamp', time.time())
                if ts > 1e10:
                    ts /= 1000
                try:
                    dist = float(s.get('ultrasonico_distancia', 0))
                except (ValueError, TypeError):
                    dist = "N/A"
                resultado.append({
                    "timestamp"          : datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S'),
                    "ultrasonico_distancia": dist,
                    "ultrasonico_digital_1": "Activo" if s.get('ultrasonido_1') == 0 else "Inactivo",
                    "ultrasonico_digital_2": "Activo" if s.get('ultrasonido_2') == 0 else "Inactivo",
                    "ultrasonico_digital_3": "Activo" if s.get('ultrasonido_3') == 0 else "Inactivo",
                    "sensor_ir"           : "Sin señal" if s.get('sensor_ir') == 0 else "Con señal",
                    "sensor_fuego_1"      : "Activo" if s.get('sensor_fuego_1') == 0 else "Inactivo",
                    "sensor_fuego_2"      : "Activo" if s.get('sensor_fuego_2') == 0 else "Inactivo",
                })
            return resultado
        except Exception as e:
            logger.error(f"[Historial] sensor_data: {e}")
            return []

    def obtener_datos_cap_sensors(self, limite=100) -> List[dict]:
        """Sensores de la gorra/mochila (MPU6050, ultrasonido, temperatura)."""
        try:
            docs = (self._db.collection('cap_sensors')
                    .order_by('timestamp', direction=firestore.Query.DESCENDING)
                    .limit(limite).stream())
            resultado = []
            for doc in docs:
                s  = doc.to_dict()
                ts = s.get('timestamp', time.time())
                if ts > 1e10:
                    ts /= 1000

                def _f(v):
                    try:    return float(v)
                    except: return "N/A"

                resultado.append({
                    "timestamp" : datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S'),
                    "acel_X"    : _f(s.get('acel_X')),
                    "acel_Y"    : _f(s.get('acel_Y')),
                    "acel_Z"    : _f(s.get('acel_Z')),
                    "colocada"  : "Sí" if s.get('colocada') else "No",
                    "temperatura": _f(s.get('temperatura')),
                    "ultrasonico": _f(s.get('ultrasonico')),
                })
            return resultado
        except Exception as e:
            logger.error(f"[Historial] cap_sensors: {e}")
            return []

    # ── NUEVO: GPS ────────────────────────────────────────────────────────────
    def obtener_gps_data(self, fuente: str = "mochila", limite=50) -> List[dict]:
        """
        Recupera historial de posiciones GPS de la colección 'gps_data'.
        Filtrada por fuente: 'mochila' o 'carrito'.
        """
        try:
            docs = (self._db.collection('gps_data')
                    .where('fuente', '==', fuente)
                    .order_by('timestamp', direction=firestore.Query.DESCENDING)
                    .limit(limite).stream())
            resultado = []
            for doc in docs:
                d  = doc.to_dict()
                ts = d.get('timestamp', time.time())
                if ts > 1e10:
                    ts /= 1000
                resultado.append({
                    "timestamp": datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S'),
                    "lat"      : d.get('lat'),
                    "lon"      : d.get('lon'),
                    "alt"      : d.get('alt'),
                    "vel_kmh"  : d.get('vel_kmh'),
                    "sats"     : d.get('sats'),
                    "valido"   : d.get('valido'),
                    "fuente"   : fuente,
                })
            return resultado
        except Exception as e:
            logger.error(f"[Historial] gps_data: {e}")
            return []

    # ── NUEVO: Eventos Safe-Path ───────────────────────────────────────────────
    def obtener_safepath_events(self, limite=100) -> List[dict]:
        """Recupera alertas/eventos de la mochila Safe-Path desde Firestore."""
        try:
            docs = (self._db.collection('safepath_events')
                    .order_by('timestamp', direction=firestore.Query.DESCENDING)
                    .limit(limite).stream())
            resultado = []
            for doc in docs:
                d  = doc.to_dict()
                ts = d.get('timestamp', time.time())
                if ts > 1e10:
                    ts /= 1000
                resultado.append({
                    "timestamp"    : datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S'),
                    "tipo"         : d.get('tipo', ''),
                    "distancia_cm" : d.get('distancia_cm'),
                    "oscuro"       : d.get('oscuro'),
                    "caida"        : d.get('caida'),
                    "temperatura"  : d.get('temperatura'),
                })
            return resultado
        except Exception as e:
            logger.error(f"[Historial] safepath_events: {e}")
            return []


# ─────────────────────────────────────────────────────────────────────────────
# PROCESADORES DE MENSAJES MQTT ENTRANTES (guardan en Firestore + emiten vía SocketIO)
# ─────────────────────────────────────────────────────────────────────────────
def _mapear_sensor_carrito(entry: dict) -> dict:
    ts = entry.get('timestamp', time.time())
    if ts > 1e10:
        ts /= 1000
    try:    dist = float(entry.get('ultrasonico_distancia', 0))
    except: dist = "N/A"
    return {
        "timestamp"             : datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S'),
        "ultrasonico_distancia" : dist,
        "ultrasonico_digital_1" : "Activo" if entry.get('ultrasonido_1') == 0 else "Inactivo",
        "ultrasonico_digital_2" : "Activo" if entry.get('ultrasonido_2') == 0 else "Inactivo",
        "ultrasonico_digital_3" : "Activo" if entry.get('ultrasonido_3') == 0 else "Inactivo",
        "sensor_ir"             : "Sin señal" if entry.get('sensor_ir') == 0 else "Con señal",
        "sensor_fuego_1"        : "Activo" if entry.get('sensor_fuego_1') == 0 else "Inactivo",
        "sensor_fuego_2"        : "Activo" if entry.get('sensor_fuego_2') == 0 else "Inactivo",
    }


def procesar_datos_sensor(payload: str):
    """RECICLADO de process_sensor_data() del SmartCap."""
    try:
        data  = json.loads(payload)
        entry = {
            'timestamp'            : data.get('timestamp', time.time()),
            'ultrasonido_1'        : data.get('ultrasonido_1'),
            'ultrasonido_2'        : data.get('ultrasonido_2'),
            'ultrasonido_3'        : data.get('ultrasonido_3'),
            'ultrasonico_distancia': data.get('ultrasonico_distancia'),
            'sensor_ir'            : data.get('sensor_ir'),
            'sensor_fuego_1'       : data.get('sensor_fuego_1'),
            'sensor_fuego_2'       : data.get('sensor_fuego_2'),
            'gps_lat'              : data.get('gps_lat'),
            'gps_lng'              : data.get('gps_lng'),
            'line_sensor_left'     : data.get('line_sensor_left'),
            'line_sensor_center'   : data.get('line_sensor_center'),
            'line_sensor_right'    : data.get('line_sensor_right'),
        }
        db.collection('sensor_data').add(entry)
        mapeado = _mapear_sensor_carrito(entry)
        sio.start_background_task(sio.emit, 'new_sensor_data', mapeado)
    except Exception as e:
        logger.error(f"[procesar_datos_sensor] {e}")


def procesar_cap_sensor(payload: str):
    """RECICLADO de process_cap_sensor_data() del SmartCap."""
    try:
        data  = json.loads(payload)
        entry = {
            'timestamp'  : data.get('timestamp', time.time()),
            'acel_X'     : data.get('acel_X'),
            'acel_Y'     : data.get('acel_Y'),
            'acel_Z'     : data.get('acel_Z'),
            'colocada'   : data.get('colocada', False),
            'temperatura': data.get('temperatura'),
            'ultrasonico': data.get('ultrasonico'),
        }
        db.collection('cap_sensors').add(entry)

        def _f(v):
            try:    return float(v)
            except: return "N/A"

        ts = entry['timestamp']
        if ts > 1e10:
            ts /= 1000
        mapeado = {
            "timestamp" : datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S'),
            "acel_X"    : _f(entry['acel_X']),
            "acel_Y"    : _f(entry['acel_Y']),
            "acel_Z"    : _f(entry['acel_Z']),
            "colocada"  : "Sí" if entry['colocada'] else "No",
            "temperatura": _f(entry['temperatura']),
            "ultrasonico": _f(entry['ultrasonico']),
        }
        sio.start_background_task(sio.emit, 'new_cap_sensor_data', mapeado)
    except Exception as e:
        logger.error(f"[procesar_cap_sensor] {e}")


def procesar_safepath_sensores(payload: str):
    """
    NUEVO: procesa telemetría de la mochila Safe-Path AI.
    Tópico: safepath/sensores
    """
    try:
        data = json.loads(payload)
        entry = {
            'timestamp'   : data.get('ts', time.time()),
            'distancia_cm': data.get('dist'),
            'oscuro'      : data.get('oscuro'),
            'caida'       : data.get('caida'),
            'temperatura' : data.get('temp'),
            'fuente'      : 'mochila',
        }
        db.collection('safepath_events').add(entry)
        sio.start_background_task(sio.emit, 'safepath_telemetria', entry)
    except Exception as e:
        logger.error(f"[procesar_safepath_sensores] {e}")


def procesar_safepath_alerta(payload: str):
    """
    NUEVO: procesa alertas críticas de la mochila (caída, colisión, etc.).
    Tópico: safepath/alertas
    """
    try:
        entry = {
            'timestamp': time.time(),
            'tipo'     : payload,
            'fuente'   : 'mochila',
        }
        db.collection('safepath_events').add(entry)
        sio.start_background_task(sio.emit, 'safepath_alerta', {'tipo': payload})
        logger.warning(f"[SafePath] ALERTA: {payload}")
    except Exception as e:
        logger.error(f"[procesar_safepath_alerta] {e}")


def procesar_gps(payload: str, fuente: str = "mochila"):
    """
    NUEVO: procesa datos GPS de la mochila o el carrito.
    Tópicos: safepath/gps | car/gps
    """
    try:
        data  = json.loads(payload)
        entry = {
            'timestamp': data.get('ts', time.time()),
            'lat'      : data.get('lat'),
            'lon'      : data.get('lon'),
            'alt'      : data.get('alt', 0),
            'vel_kmh'  : data.get('vel_kmh', 0),
            'sats'     : data.get('sats', 0),
            'valido'   : data.get('valido', False),
            'fuente'   : fuente,
        }
        db.collection('gps_data').add(entry)
        sio.start_background_task(sio.emit, 'gps_update',
                                  {**entry, 'fuente': fuente})
    except Exception as e:
        logger.error(f"[procesar_gps] {e}")


# ─────────────────────────────────────────────────────────────────────────────
# MANEJADOR DE EXCEPCIONES HTTP (reciclado de SmartCap)
# ─────────────────────────────────────────────────────────────────────────────
@fastapi_app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    if exc.status_code == 401:
        if "text/html" in request.headers.get("accept", ""):
            return RedirectResponse(url="/login?message=Sesion%20finalizada",
                                    status_code=303)
    return JSONResponse(status_code=exc.status_code,
                        content={"detail": exc.detail})


# ─────────────────────────────────────────────────────────────────────────────
# ENDPOINTS DE AUTENTICACIÓN (reciclados de SmartCap)
# ─────────────────────────────────────────────────────────────────────────────
@fastapi_app.get("/", include_in_schema=False)
async def root():
    return RedirectResponse(url="/login")


@fastapi_app.get("/login", response_class=HTMLResponse)
async def login_get(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@fastapi_app.post("/login", response_class=RedirectResponse)
async def login_post(request: Request,
                     username: str = Form(...),
                     password: str = Form(...)):
    user = authenticate_user(username.strip(), password.strip())
    if not user:
        return templates.TemplateResponse(
            "login.html",
            {"request": request, "error": "Usuario o contraseña incorrectos."},
            status_code=401
        )
    token = create_access_token(
        data={"sub": user.username},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    resp = RedirectResponse(url="/menu", status_code=303)
    resp.set_cookie("access_token", f"Bearer {token}",
                    httponly=True,
                    max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
                    samesite="lax", secure=True)
    return resp


@fastapi_app.get("/logout", response_class=RedirectResponse)
async def logout():
    resp = RedirectResponse(url="/login", status_code=303)
    resp.delete_cookie("access_token", path="/")
    return resp


# ─────────────────────────────────────────────────────────────────────────────
# ENDPOINTS HTML (reciclados de SmartCap + nuevos Safe-Path)
# ─────────────────────────────────────────────────────────────────────────────
@fastapi_app.get("/menu",             response_class=HTMLResponse)
async def menu(request: Request,          u=Depends(get_current_user)):
    return templates.TemplateResponse("menu.html", {"request": request, "user": u.username})

@fastapi_app.get("/gps",              response_class=HTMLResponse)
async def gps_view(request: Request,      u=Depends(get_current_user)):
    return templates.TemplateResponse("gps.html", {"request": request, "user": u.username})

@fastapi_app.get("/historial",        response_class=HTMLResponse)
async def historial_view(request: Request, u=Depends(get_current_user)):
    return templates.TemplateResponse("historial.html", {"request": request, "user": u.username})

@fastapi_app.get("/objetos_reconocidos", response_class=HTMLResponse)
async def objetos_view(request: Request,  u=Depends(get_current_user)):
    return templates.TemplateResponse("objetos_reconocidos.html",
                                      {"request": request, "user": u.username})

@fastapi_app.get("/add_registration", response_class=HTMLResponse)
async def add_reg_form(request: Request,  u=Depends(get_current_user)):
    return templates.TemplateResponse("add_registration.html",
                                      {"request": request, "user": u.username})

@fastapi_app.get("/safepath_dashboard", response_class=HTMLResponse)
async def safepath_dashboard(request: Request, u=Depends(get_current_user)):
    """NUEVO: Dashboard específico para la mochila Safe-Path AI."""
    return templates.TemplateResponse("safepath_dashboard.html",
                                      {"request": request, "user": u.username})


# ─────────────────────────────────────────────────────────────────────────────
# ENDPOINTS MQTT — CONTROL DEL CARRITO (reciclados de SmartCap)
# ─────────────────────────────────────────────────────────────────────────────
@fastapi_app.post("/send_command", response_class=JSONResponse)
async def send_command(command: dict, u=Depends(get_current_user)):
    """Envía un comando al carrito o la mochila vía MQTT."""
    cmd = command.get("command", "")
    if not cmd:
        raise HTTPException(400, "No se proporcionó comando.")

    CMDS_GORRA   = {'alto_movimiento_gorra', 'reanudar_movimiento_gorra'}
    CMDS_FLASH   = {'flash_on', 'flash_off'}
    CMDS_SP      = {'silencio', 'reanudar', 'test_buzzer', 'test_vibra'}  # NUEVO Safe-Path

    if cmd in CMDS_GORRA:
        topic, payload = T_CAR_GORRA, cmd
    elif cmd in CMDS_FLASH:
        topic, payload = T_CAR_FLASH, 'on' if cmd == 'flash_on' else 'off'
    elif cmd in CMDS_SP:
        topic, payload = T_SP_CMDS, cmd
    else:
        topic, payload = T_CAR_CMDS, cmd

    _publicar(topic, payload)
    await sio.emit('mqtt_command', {'topic': topic, 'command': payload})
    return {"status": "success"}


@fastapi_app.post("/set_power", response_class=JSONResponse)
async def set_power(power: dict, u=Depends(get_current_user)):
    """RECICLADO de SmartCap: controla la potencia de los motores del carrito."""
    val = power.get("power")
    if val is None:
        raise HTTPException(400, "Valor de potencia requerido.")
    try:
        p = int(val)
        if not 0 <= p <= 65535:
            raise HTTPException(400, "Rango: 0-65535.")
    except ValueError:
        raise HTTPException(400, "Valor inválido.")
    _publicar(T_CAR_POWER, str(p))
    await sio.emit('mqtt_set_power', {'power': p})
    return {"status": "success"}


# ─────────────────────────────────────────────────────────────────────────────
# ENDPOINTS DE DATOS DE SENSORES (reciclados de SmartCap)
# ─────────────────────────────────────────────────────────────────────────────
@fastapi_app.post("/sensor_data",    response_class=JSONResponse)
async def post_sensor_data(data: dict, u=Depends(get_current_user)):
    """Recibe datos del carrito vía HTTP POST (alternativo a MQTT)."""
    if not data:
        raise HTTPException(400, "Sin datos.")
    procesar_datos_sensor(json.dumps(data))
    return {"status": "success"}


@fastapi_app.get("/get_sensor_data",   response_class=JSONResponse)
async def get_sensor_data(u=Depends(get_current_user)):
    return Historial(db).obtener_datos_sensor()


@fastapi_app.post("/cap_sensor_data",  response_class=JSONResponse)
async def post_cap_sensor(data: dict,  u=Depends(get_current_user)):
    if not data:
        raise HTTPException(400, "Sin datos.")
    procesar_cap_sensor(json.dumps(data))
    return {"status": "success"}


@fastapi_app.get("/get_cap_sensor_data", response_class=JSONResponse)
async def get_cap_sensor_data(u=Depends(get_current_user)):
    return Historial(db).obtener_datos_cap_sensors()


# ─────────────────────────────────────────────────────────────────────────────
# ENDPOINTS GPS (NUEVO)
# ─────────────────────────────────────────────────────────────────────────────
@fastapi_app.post("/gps_data", response_class=JSONResponse)
async def post_gps_data(data: dict, u=Depends(get_current_user)):
    """Recibe coordenadas GPS de cualquier dispositivo vía HTTP."""
    fuente = data.pop('fuente', 'mochila')
    procesar_gps(json.dumps({**data, 'fuente': fuente}), fuente=fuente)
    return {"status": "success"}


@fastapi_app.get("/get_gps_data", response_class=JSONResponse)
async def get_gps_data(fuente: str = "mochila", u=Depends(get_current_user)):
    """Historial de posiciones GPS filtrado por dispositivo."""
    return Historial(db).obtener_gps_data(fuente=fuente)


# ─────────────────────────────────────────────────────────────────────────────
# ENDPOINTS SAFE-PATH (NUEVOS)
# ─────────────────────────────────────────────────────────────────────────────
@fastapi_app.post("/safepath_event", response_class=JSONResponse)
async def post_safepath_event(data: dict, u=Depends(get_current_user)):
    """Recibe eventos de la mochila Safe-Path vía HTTP (alternativo a MQTT)."""
    tipo = data.get('tipo', 'telemetria')
    if tipo == 'telemetria':
        procesar_safepath_sensores(json.dumps(data))
    else:
        procesar_safepath_alerta(tipo)
    return {"status": "success"}


@fastapi_app.get("/get_safepath_events", response_class=JSONResponse)
async def get_safepath_events(u=Depends(get_current_user)):
    return Historial(db).obtener_safepath_events()


@fastapi_app.post("/safepath_command", response_class=JSONResponse)
async def safepath_command(data: dict, u=Depends(get_current_user)):
    """Envía un comando directamente a la mochila Safe-Path."""
    cmd = data.get("command", "")
    if not cmd:
        raise HTTPException(400, "Comando requerido.")
    _publicar(T_SP_CMDS, cmd)
    return {"status": "success", "publicado_en": T_SP_CMDS}


# ─────────────────────────────────────────────────────────────────────────────
# ENDPOINTS DE STREAMING VIDEO (reciclados de SmartCap + Safe-Path mochila)
# ─────────────────────────────────────────────────────────────────────────────
frame_lock_carro   = asyncio.Lock()
frame_lock_gorra   = asyncio.Lock()
frame_lock_mochila = asyncio.Lock()   # NUEVO: mochila Safe-Path

latest_frame_carro   = None
latest_frame_gorra   = None
latest_frame_mochila = None


@fastapi_app.post("/upload_frame_carro")
async def upload_frame_carro(request: Request):
    """
    RECICLADO de SmartCap: recibe frames del carrito, aplica detección
    de objetos SSD MobileNet y los hace disponibles para streaming.
    """
    global latest_frame_carro
    img_data = await request.body()
    async with frame_lock_carro:
        nparr = np.frombuffer(img_data, np.uint8)
        img   = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        img_procesada, etiquetas = detector_objetos.procesar_frame(img)
        _, buf = cv2.imencode('.jpg', img_procesada)
        latest_frame_carro = buf.tobytes()
        if etiquetas:
            logger.info(f"[Carrito] Objetos detectados: {etiquetas}")
    return {"status": "success"}


@fastapi_app.post("/upload_frame_gorra")
async def upload_frame_gorra(request: Request):
    """
    RECICLADO de SmartCap: recibe frames de la gorra, aplica reconocimiento
    facial y publica el nombre detectado en MQTT.
    """
    global latest_frame_gorra
    img_data = await request.body()
    async with frame_lock_gorra:
        nparr = np.frombuffer(img_data, np.uint8)
        img   = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        img_procesada, nombres = reconocedor_facial.procesar_frame(img)
        _, buf = cv2.imencode('.jpg', img_procesada)
        latest_frame_gorra = buf.tobytes()
        for nombre in nombres:
            _publicar(T_GORRA_ROSTROS, nombre)
            logger.info(f"[Gorra] Rostro: {nombre}")
    return {"status": "success"}


@fastapi_app.post("/upload_frame_mochila")
async def upload_frame_mochila(request: Request):
    """
    NUEVO: endpoint para la ESP32-CAM de la mochila Safe-Path AI.
    Aplica reconocimiento facial (YOLOv8 en versión futura) y
    publica resultado en safepath/reconocido.
    """
    global latest_frame_mochila
    img_data = await request.body()
    async with frame_lock_mochila:
        nparr = np.frombuffer(img_data, np.uint8)
        img   = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        img_procesada, nombres = reconocedor_facial.procesar_frame(img)
        _, buf = cv2.imencode('.jpg', img_procesada)
        latest_frame_mochila = buf.tobytes()
        for nombre in nombres:
            _publicar(T_SP_RECONOCIDO, nombre)
            logger.info(f"[Mochila] Persona: {nombre}")
    return {"status": "success"}


def _stream_generator(get_frame, lock):
    """Generador genérico de MJPEG para los tres endpoints de video."""
    async def stream():
        while True:
            async with lock:
                frame = get_frame()
            if frame:
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
            await asyncio.sleep(0.05)
    return stream


@fastapi_app.get("/video_feed_carro")
async def video_feed_carro():
    return StreamingResponse(
        _stream_generator(lambda: latest_frame_carro, frame_lock_carro)(),
        media_type='multipart/x-mixed-replace; boundary=frame')


@fastapi_app.get("/video_feed_gorra")
async def video_feed_gorra():
    return StreamingResponse(
        _stream_generator(lambda: latest_frame_gorra, frame_lock_gorra)(),
        media_type='multipart/x-mixed-replace; boundary=frame')


@fastapi_app.get("/video_feed_mochila")
async def video_feed_mochila():
    """NUEVO: streaming de la cámara de la mochila Safe-Path."""
    return StreamingResponse(
        _stream_generator(lambda: latest_frame_mochila, frame_lock_mochila)(),
        media_type='multipart/x-mixed-replace; boundary=frame')


# ─────────────────────────────────────────────────────────────────────────────
# ENDPOINTS CRUD DE RECONOCIMIENTO (reciclados de SmartCap + gestión de modelos)
# ─────────────────────────────────────────────────────────────────────────────
@fastapi_app.get("/get_recognized_objects", response_class=JSONResponse)
async def get_recognized_objects(u=Depends(get_current_user)):
    """RECICLADO de SmartCap: lista patrones de reconocimiento registrados."""
    try:
        docs = (db.collection('recognition_patterns')
                .order_by('created_at', direction=firestore.Query.DESCENDING)
                .limit(100).stream())
        resultado = []
        for doc in docs:
            obj  = doc.to_dict()
            dpath = obj.get('directory_path', '')
            imgs  = sorted(glob.glob(os.path.join(dpath, '*'))) if dpath else []
            primera_url = (f"/patterns/{os.path.relpath(imgs[0], 'patterns').replace(os.sep, '/')}"
                           if imgs else None)
            resultado.append({
                "id"         : doc.id,
                "object_name": obj.get('name', 'Desconocido'),
                "description": obj.get('type', ''),
                "image_url"  : primera_url,
            })
        return resultado
    except Exception as e:
        logger.exception(f"get_recognized_objects: {e}")
        raise HTTPException(500, "Error interno.")


@fastapi_app.post("/create_recognition_pattern", response_class=JSONResponse)
async def create_recognition_pattern(request: Request,
                                     background_tasks: BackgroundTasks,
                                     u=Depends(get_current_user)):
    """
    NUEVO endpoint unificado para crear patrones.
    Acepta multipart/form-data con campos: type, name, images[].
    Equivale al /create_face_pattern del recognition.py original,
    movido aquí para centralizar la lógica en app.py.
    """
    from fastapi import UploadFile, File
    form   = await request.form()
    tipo   = str(form.get('type', '')).lower()
    nombre = str(form.get('name', ''))
    imagenes = form.getlist('images')

    if tipo not in ('persona', 'objeto'):
        raise HTTPException(400, "type debe ser 'persona' o 'objeto'.")
    if len(imagenes) < 20:
        raise HTTPException(400, "Se requieren al menos 20 imágenes.")

    nombre_seguro = sanitizar_nombre(nombre)
    if not nombre_seguro:
        raise HTTPException(400, "Nombre inválido.")

    dir_base  = FACES_DIR if tipo == 'persona' else OBJECTS_DIR
    dir_usuario = os.path.join(dir_base, nombre_seguro)
    os.makedirs(dir_usuario, exist_ok=True)

    archivos_guardados = []
    for img in imagenes:
        nombre_arch = sanitizar_nombre_archivo(img.filename)
        if not nombre_arch:
            continue
        ruta = os.path.join(dir_usuario, nombre_arch)
        with open(ruta, 'wb') as f:
            shutil.copyfileobj(img.file, f)
        archivos_guardados.append(ruta)

    if len(archivos_guardados) < 20:
        raise HTTPException(400, "No se guardaron suficientes imágenes.")

    # Entrenar en background
    if tipo == 'persona':
        background_tasks.add_task(entrenar_modelo_facial, reconocedor_facial)
    else:
        background_tasks.add_task(entrenar_modelo_objetos, reconocedor_objetos)

    guardar_patron_en_firebase(nombre, tipo, dir_usuario, len(archivos_guardados))

    await sio.emit('new_recognized_object', {
        'object_name': nombre,
        'description': tipo,
        'image_url'  : None,
    })
    return {"status": "success",
            "message": f"Patrón de {tipo} '{nombre}' creado con "
                       f"{len(archivos_guardados)} imágenes."}


@fastapi_app.delete("/recognized_object/{id}", response_class=JSONResponse)
async def delete_recognized_object(id: str,
                                   background_tasks: BackgroundTasks,
                                   u=Depends(get_current_user)):
    """RECICLADO de SmartCap: elimina patrón + imágenes + reentrenamiento."""
    doc_ref = db.collection('recognition_patterns').document(id)
    doc     = doc_ref.get()
    if not doc.exists:
        raise HTTPException(404, "Registro no encontrado.")

    obj   = doc.to_dict()
    dpath = obj.get('directory_path', '')
    tipo  = obj.get('type', '').lower()

    # Eliminar imágenes y directorio
    if dpath and os.path.isdir(dpath):
        shutil.rmtree(dpath, ignore_errors=True)

    doc_ref.delete()

    # Reentrenamiento en background
    if tipo == 'persona':
        background_tasks.add_task(_gestionar_modelo_facial)
    elif tipo == 'objeto':
        background_tasks.add_task(_gestionar_modelo_objetos)

    await sio.emit('delete_recognized_object', {'id': id})
    return {"status": "success"}


def _gestionar_modelo_facial():
    """RECICLADO de gestionar_modelo_facial() del SmartCap."""
    restantes = list(
        db.collection('recognition_patterns')
          .where('type', '==', 'persona').stream()
    )
    if restantes:
        try:
            entrenar_modelo_facial(reconocedor_facial)
        except Exception as e:
            logger.error(f"[gestionar_modelo_facial] {e}")
    else:
        pkl = os.path.join(PATTERNS_DIR, 'face_encodings.pkl')
        if os.path.exists(pkl):
            os.remove(pkl)
        reconocedor_facial.recargar()


def _gestionar_modelo_objetos():
    """RECICLADO de gestionar_modelo_objetos() del SmartCap."""
    restantes = list(
        db.collection('recognition_patterns')
          .where('type', '==', 'objeto').stream()
    )
    if restantes:
        try:
            entrenar_modelo_objetos(reconocedor_objetos)
        except Exception as e:
            logger.error(f"[gestionar_modelo_objetos] {e}")
    else:
        pkl = os.path.join(PATTERNS_DIR, 'object_encodings.pkl')
        if os.path.exists(pkl):
            os.remove(pkl)
        reconocedor_objetos.recargar()


# ─────────────────────────────────────────────────────────────────────────────
# SOCKETIO EVENTOS (reciclados de SmartCap)
# ─────────────────────────────────────────────────────────────────────────────
@sio.event
async def connect(sid, environ):
    logger.info(f"[SocketIO] Cliente conectado: {sid}")
    await sio.emit('connection_response',
                   {'data': 'Conectado al servidor Safe-Path AI'}, to=sid)


@sio.event
async def disconnect(sid):
    logger.info(f"[SocketIO] Cliente desconectado: {sid}")


# ─────────────────────────────────────────────────────────────────────────────
# CATCH-ALL (reciclado de SmartCap)
# ─────────────────────────────────────────────────────────────────────────────
@fastapi_app.get("/{full_path:path}", include_in_schema=False)
async def catch_all(full_path: str, request: Request):
    if full_path.startswith("socket.io"):
        raise HTTPException(404)
    return RedirectResponse(url="/login?message=Ruta%20no%20encontrada.",
                            status_code=303)


# ─────────────────────────────────────────────────────────────────────────────
# PUNTO DE ENTRADA
# ─────────────────────────────────────────────────────────────────────────────
if __name__ == '__main__':
    import uvicorn
    logger.info("Iniciando Safe-Path AI Server en puerto 8080...")
    try:
        uvicorn.run(app, host='0.0.0.0', port=8080, log_level="debug")
    except Exception as e:
        logger.exception(f"Error crítico: {e}")
        mqtt_client.disconnect()
        mqtt_client.loop_stop()
