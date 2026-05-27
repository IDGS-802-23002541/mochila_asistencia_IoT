# Safe-Path AI 🦯
### Sistema de Navegación Aumentada y Asistencia Cognitiva
**Instituto Tecnológico de León — TecNM | Sistemas Programables 2025**

---

## Descripción

Safe-Path AI es un sistema IoT portátil para personas con discapacidad visual.
Combina detección de obstáculos por hardware con inteligencia artificial (reconocimiento
facial + detección de objetos SSD MobileNet) para proporcionar retroalimentación de voz,
háptica y sonora en tiempo real.

Evoluciona directamente del proyecto **SmartCap** (ITL, dic. 2024), reciclando y
mejorando sus bibliotecas de hardware y servidor.

---

## Arquitectura del sistema

```
┌─────────────────────────────────────────────────────────────┐
│  CAPA EDGE  (ESP32-CAM MicroPython)                         │
│  ┌─────────────┐  ┌──────────────┐  ┌──────────────────┐   │
│  │ SensorBox   │  │ ActuatorBox  │  │ GPSManager       │   │
│  │ HC-SR04     │  │ DFPlayer     │  │ Ublox NEO-6M     │   │
│  │ LDR         │  │ Motor vibrad.│  │ NMEA parser      │   │
│  │ MPU6050     │  │ Buzzer       │  │ Historial GPS    │   │
│  └──────┬──────┘  └──────┬───────┘  └────────┬─────────┘   │
│         └────────────────┼─────────────────────┘            │
│                   main.py (asyncio)                         │
│            MQTTManager  │  FirebaseClient                   │
└─────────────────────────┼───────────────────────────────────┘
                          │ MQTT / HTTP
┌─────────────────────────▼───────────────────────────────────┐
│  CAPA SERVIDOR  (Python FastAPI)                            │
│  app.py                                                     │
│  ├── recognition.py  → FaceRecognizer + ObjectDetector      │
│  ├── firebase_init.py → Firestore client                    │
│  ├── add_user.py      → Gestión de usuarios                 │
│  └── SocketIO         → Dashboard tiempo real              │
└─────────────────────────┬───────────────────────────────────┘
                          │ Firebase Firestore
┌─────────────────────────▼───────────────────────────────────┐
│  CAPA DATOS  (Firebase Firestore)                           │
│  ├── sensor_data        → carrito (ultrasonido, IR, fuego)  │
│  ├── cap_sensors        → gorra/mochila (MPU6050, US, temp) │
│  ├── safepath_events    → alertas y telemetría mochila      │
│  ├── gps_data           → posiciones GPS (carrito+mochila)  │
│  ├── recognition_patterns → personas y objetos registrados  │
│  └── users              → autenticación JWT                 │
└─────────────────────────────────────────────────────────────┘
```

---

## Estructura de archivos

```
safe_path_ai/
├── E1_HAL/
│   ├── dispositivos.py      ← HAL completa (SensorBox, ActuatorBox,
│   │                           MQTTManager, FirebaseClient)
│   ├── gps_manager.py       ← GPSManager + loop_gps()
│   ├── test_hardware.py     ← Suite de pruebas E1
│   └── test_gps.py          ← Suite de pruebas GPS (offline + online)
│
├── E2_MQTT/
│   └── main.py              ← Firmware principal (asyncio, 5 corutinas)
│
└── servidor/
    ├── app.py               ← FastAPI + SocketIO + MQTT + Streaming
    ├── recognition.py       ← FaceRecognizer, ObjectDetector, entrenamiento
    ├── firebase_init.py     ← Inicialización Firebase Admin SDK
    ├── add_user.py          ← CRUD de usuarios Firestore
    ├── requirements.txt     ← Dependencias Python
    ├── credentials/
    │   └── serviceAccountKey.json   ← Descargar desde Firebase Console
    ├── patterns/
    │   ├── faces/           ← Imágenes de personas (una carpeta por persona)
    │   ├── objects/         ← Imágenes de objetos (una carpeta por objeto)
    │   ├── face_encodings.pkl       ← Generado automáticamente al entrenar
    │   ├── object_encodings.pkl     ← Generado automáticamente al entrenar
    │   ├── coco.names               ← Etiquetas COCO para SSD MobileNet
    │   ├── ssd_mobilenet_v3_large_coco_2020_01_14.pbtxt
    │   └── frozen_inference_graph.pb
    ├── static/              ← CSS, JS, imágenes del dashboard
    └── templates/           ← HTML Jinja2
        ├── login.html
        ├── menu.html
        ├── gps.html
        ├── historial.html
        ├── objetos_reconocidos.html
        ├── add_registration.html
        └── safepath_dashboard.html
```

---

## Instalación

### 1. Servidor Python

```bash
# Clonar / descomprimir el proyecto
cd servidor/

# Crear entorno virtual (recomendado)
python3 -m venv venv
source venv/bin/activate   # Linux/Mac
venv\Scripts\activate      # Windows

# Instalar dependencias
pip install -r requirements.txt

# Descargar modelos SSD MobileNet (ejecutar una vez)
cd patterns/
wget https://raw.githubusercontent.com/PINTO0309/MobileNet-SSD-RealSense/master/coco.names
wget https://raw.githubusercontent.com/opencv/opencv/master/samples/dnn/face_detector/deploy.prototxt
# Modelo completo: buscar "ssd_mobilenet_v3_large_coco_2020_01_14" en el repositorio de OpenCV

# Agregar credenciales de Firebase
# Descargar serviceAccountKey.json desde:
# Firebase Console → Tu proyecto → Configuración → Cuentas de servicio → Generar clave privada
cp ~/Downloads/serviceAccountKey.json credentials/

# Crear primer usuario administrador
python add_user.py
# Seleccionar opción 1 → Crear usuario: admin / admin1234

# Iniciar servidor
uvicorn app:app --host 0.0.0.0 --port 8080 --reload
```

### 2. Firmware ESP32-CAM (MicroPython)

```
Archivos a copiar a la ESP32-CAM (con Thonny o ampy):
  dispositivos.py
  gps_manager.py
  main.py          ← (main_E2.py renombrado)
  hcsr04.py        ← del proyecto SmartCap
  imu.py           ← del proyecto SmartCap
  vector3d.py      ← del proyecto SmartCap
```

Editar en `main.py` (E2_MQTT):
```python
REDES_WIFI = [("TU_RED", "TU_CONTRASENA")]
MQTT_BROKER = "IP_DE_TU_SERVIDOR"
```

---

## Tópicos MQTT

| Dispositivo | Dirección | Tópico | Contenido |
|---|---|---|---|
| Mochila | Publica | `safepath/sensores` | JSON telemetría cada 5 s |
| Mochila | Publica | `safepath/alertas` | String de alerta crítica |
| Mochila | Publica | `safepath/gps` | JSON posición GPS |
| Mochila | Suscribe | `safepath/comandos` | silencio, reanudar, test |
| Mochila | Suscribe | `safepath/reconocido` | nombre persona detectada |
| Carrito | Publica | `car/sensor_data` | JSON sensores carrito |
| Carrito | Publica | `car/gps` | JSON posición GPS carrito |
| Carrito | Suscribe | `car/commands` | adelante, atras, izq, der |
| Carrito | Suscribe | `car/set_power` | 0-65535 |
| Gorra | Publica | `cap/faces` | nombre persona reconocida |

---

## Colecciones Firestore

| Colección | Campos principales | Fuente |
|---|---|---|
| `sensor_data` | timestamp, ultrasonico_distancia, sensor_ir, sensor_fuego_1/2, gps_lat/lng | Carrito |
| `cap_sensors` | timestamp, acel_X/Y/Z, colocada, temperatura, ultrasonico | Gorra/Mochila |
| `safepath_events` | timestamp, tipo, distancia_cm, oscuro, caida, temperatura | Mochila |
| `gps_data` | timestamp, lat, lon, alt, vel_kmh, sats, valido, fuente | Carrito + Mochila |
| `recognition_patterns` | name, type, directory_path, created_at, image_count | Servidor |
| `users` | username, password_hash, created_at | add_user.py |

---

## Endpoints del servidor

### Autenticación
| Método | Ruta | Descripción |
|---|---|---|
| GET | `/login` | Formulario de login |
| POST | `/login` | Autenticar y crear cookie JWT |
| GET | `/logout` | Cerrar sesión |

### Vistas HTML
| Método | Ruta | Descripción |
|---|---|---|
| GET | `/menu` | Panel de control principal (carrito) |
| GET | `/gps` | Mapa GPS en tiempo real |
| GET | `/historial` | Historial de sensores |
| GET | `/objetos_reconocidos` | Galería de patrones registrados |
| GET | `/safepath_dashboard` | Dashboard exclusivo Safe-Path AI |

### Streaming de video
| Método | Ruta | Descripción |
|---|---|---|
| POST | `/upload_frame_carro` | Recibe frames del carrito (detección objetos) |
| POST | `/upload_frame_gorra` | Recibe frames de la gorra (reconocimiento facial) |
| POST | `/upload_frame_mochila` | Recibe frames de la mochila Safe-Path |
| GET | `/video_feed_carro` | Stream MJPEG del carrito |
| GET | `/video_feed_gorra` | Stream MJPEG de la gorra |
| GET | `/video_feed_mochila` | Stream MJPEG de la mochila |

### Sensores y datos
| Método | Ruta | Descripción |
|---|---|---|
| POST | `/sensor_data` | Recibe datos del carrito vía HTTP |
| GET | `/get_sensor_data` | Historial de sensores del carrito |
| POST | `/cap_sensor_data` | Recibe datos de la gorra vía HTTP |
| GET | `/get_cap_sensor_data` | Historial de sensores de la gorra |
| POST | `/gps_data` | Recibe posición GPS vía HTTP |
| GET | `/get_gps_data?fuente=mochila` | Historial GPS filtrado por dispositivo |
| POST | `/safepath_event` | Recibe evento/alerta de la mochila |
| GET | `/get_safepath_events` | Historial de eventos Safe-Path |

### Control MQTT
| Método | Ruta | Descripción |
|---|---|---|
| POST | `/send_command` | Envía comando a carrito o mochila |
| POST | `/set_power` | Ajusta potencia motores del carrito |
| POST | `/safepath_command` | Envía comando directo a la mochila |

### Reconocimiento
| Método | Ruta | Descripción |
|---|---|---|
| GET | `/get_recognized_objects` | Lista patrones registrados |
| POST | `/create_recognition_pattern` | Crea patrón (persona u objeto) + reentrenamiento |
| DELETE | `/recognized_object/{id}` | Elimina patrón + reentrenamiento |

---

## Eventos SocketIO

| Evento | Dirección | Descripción |
|---|---|---|
| `connection_response` | servidor → cliente | Confirmación de conexión |
| `mqtt_command` | servidor → cliente | Comando MQTT recibido (carrito) |
| `mqtt_command_gorra` | servidor → cliente | Comando MQTT de la gorra |
| `new_sensor_data` | servidor → cliente | Nuevos datos del carrito |
| `new_cap_sensor_data` | servidor → cliente | Nuevos datos de la gorra |
| `safepath_telemetria` | servidor → cliente | Telemetría de la mochila |
| `safepath_alerta` | servidor → cliente | Alerta crítica de la mochila |
| `gps_update` | servidor → cliente | Nueva posición GPS |
| `rostro_reconocido` | servidor → cliente | Persona identificada |
| `new_recognized_object` | servidor → cliente | Nuevo patrón creado |
| `delete_recognized_object` | servidor → cliente | Patrón eliminado |

---

## Reciclaje de código — SmartCap → Safe-Path AI

| SmartCap (2024) | Safe-Path AI (2025) | Tipo de cambio |
|---|---|---|
| `hcsr04.py` | Importado en `SensorBox` | Sin cambios |
| `imu.py` + `vector3d.py` | Importado en `SensorBox` | Sin cambios |
| `bocina.py` | Reemplazado por `ActuatorBox.DFPlayer` | Reemplazo |
| `SmartCapFinal.py` (~500 líneas) | `main.py` (~130 líneas) + HAL | Refactorización |
| `app.py` SmartCap | `app.py` Safe-Path AI | Extensión (+GPS, +Safe-Path, +Mochila) |
| `recognition.py` SmartCap | `recognition.py` Safe-Path AI | Encapsulado en clases |
| `firebase_init.py` SmartCap | `firebase_init.py` Safe-Path AI | Sin cambios |
| `add_user.py` SmartCap | `add_user.py` Safe-Path AI | + update, delete, list |
| `final.py` Carrito (GPS) | `gps_manager.py` | Encapsulado en clase |
| `final.py` Carrito (MQTT) | `MQTTManager` en `dispositivos.py` | Encapsulado |

---

## Créditos

- **Proyecto base**: SmartCap — Edgar Hernández, Marco Conriquez, Oscar Ramírez (ITL, 2024)
- **Proyecto carrito**: Blanca Contreras, Danna Quijas, Juan Diego Rocha, Aldo Moreno (ITL, 2024)
- **Safe-Path AI**: [Nombres del equipo] (ITL, 2025)
- **Asesora**: Ma. Verónica Tapia Ibarra — Sistemas Programables, TecNM / ITL
