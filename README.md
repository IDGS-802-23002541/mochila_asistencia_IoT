# 👁️ Vision Guard

> Sistema IoT portátil de asistencia y diagnóstico de accesibilidad para personas con discapacidad visual.

## 📌 Descripción

Vision Guard es un sistema IoT orientado al monitoreo de recorridos y a la identificación de condiciones de riesgo en espacios de una institución educativa.

El sistema utiliza una mochila/cangurera equipada con sensores para detectar obstáculos, tropiezos y caídas, registrar recorridos y obtener información de ubicación. Los datos generados son procesados mediante un pipeline ETL y análisis descriptivo para identificar zonas de riesgo y generar indicadores de accesibilidad.

El proyecto tiene un enfoque **descriptivo y diagnóstico**: transforma datos de sensores en información útil para apoyar la toma de decisiones institucionales.

## 🎯 Objetivo

Desarrollar un sistema IoT portátil de asistencia para personas con discapacidad visual, mediante una mochila/cangurera equipada con sensores ultrasónicos, acelerómetro y geolocalización, integrada con aplicaciones móvil y web para el monitoreo y análisis de recorridos e incidencias.

## 💡 Problemática

Obstáculos, banquetas irregulares, ramas, camellones sin señalización y otras condiciones físicas pueden representar barreras para la movilidad de personas con discapacidad visual.

Vision Guard busca recopilar evidencia directamente de los recorridos realizados y convertirla en información que permita identificar problemas de accesibilidad y priorizar zonas de atención.

---

# 🏗️ Arquitectura

```text
┌──────────────────────────┐
│       Dispositivo IoT    │
│          ESP32           │
│ HC-SR04 | MPU6050 | IR  │
│          GPS             │
└────────────┬─────────────┘
             │
             ▼
┌──────────────────────────┐
│     Comunicación IoT     │
│        MQTT / WiFi       │
└────────────┬─────────────┘
             │
             ▼
┌──────────────────────────┐
│         Backend           │
│       API / Servicios     │
└────────────┬─────────────┘
             │
             ▼
┌──────────────────────────┐
│    Base de datos         │
│   Esquema Operativo      │
└────────────┬─────────────┘
             │
             ▼
┌──────────────────────────┐
│       ETL / KDD          │
│ Python + Pandas + SQL    │
│ DBSCAN + IAZ + ML        │
└────────────┬─────────────┘
             │
             ▼
┌──────────────────────────┐
│      Dashboard Web       │
│ Angular + Chart.js       │
│ Leaflet + OpenStreetMap  │
└──────────────────────────┘
```

## 🔌 Hardware

| Componente                 | Función                      |
| -------------------------- | ---------------------------- |
| ESP32                      | Procesamiento y comunicación |
| HC-SR04                    | Detección de obstáculos      |
| MPU6050                    | Aceleración e impactos       |
| Sensores infrarrojos       | Detección complementaria     |
| GPS NEO-6M                 | Coordenadas geográficas      |
| Buzzer / vibración / audio | Alertas al usuario           |

## 📡 Comunicación

Los datos de los sensores se estructuran en **JSON** y se transmiten mediante WiFi utilizando **MQTT sobre TCP/IP**.

Los eventos pueden incluir fecha y hora, coordenadas, distancia, tipo de evento, severidad y lecturas de sensores.

---

# 🖥️ Backend

El backend proporciona los servicios necesarios para comunicar los componentes del sistema y administrar la información.

Sus principales responsabilidades son:

- Gestión de recorridos.
- Registro de eventos.
- Consulta de información.
- Comunicación con la base de datos.
- Exposición de datos para el dashboard.

**Tecnología principal:** ASP.NET Core / .NET y C#.

---

# 📱 Aplicación móvil

La aplicación móvil está desarrollada con **Kotlin** y permite interactuar con el sistema durante los recorridos.

Funciones principales:

- Vinculación con el dispositivo.
- Inicio y finalización de recorridos.
- Monitoreo de información.
- Consulta de eventos.
- Recepción de alertas.

---

# 🌐 Dashboard Web

El dashboard está desarrollado con **Angular** y permite consultar y visualizar los resultados del análisis.

### Visualizaciones

- 🗺️ **Mapa de calor:** representa geográficamente las zonas de riesgo.
- 📊 **IAZ por zona:** muestra el Índice de Accesibilidad por Zona.
- 🍩 **Distribución de severidad:** muestra eventos Baja, Media y Crítica.
- 📝 **Interpretación:** genera un resumen textual de los principales resultados.

### Tecnologías

- Angular
- TypeScript
- Chart.js
- Leaflet
- leaflet.heat
- OpenStreetMap

---

# 🗄️ Base de datos

El proyecto utiliza **SQL Server** para el almacenamiento histórico y analítico.

El Data Warehouse utiliza un **modelo estrella (Star Schema)**.

### Tabla de hechos

`Hechos_Incidencias`

Contiene información como:

- Identificador de incidencia.
- Usuario.
- Ubicación.
- Tiempo.
- Distancia del obstáculo.
- Magnitud del impacto.
- Duración de alerta.
- Latitud y longitud.

### Dimensiones

- `Dim_Usuario`
- `Dim_Zona`
- `Dim_Tiempo`
- `Dim_Alerta`

---

# 🔄 Flujo de datos

```text
Sensores
   ↓
ESP32
   ↓
MQTT / WiFi
   ↓
Backend
   ↓
Base de datos operativa
   ↓
ETL
   ↓
Data Warehouse
   ↓
API
   ↓
Dashboard Angular
```

---

# 🧠 ETL y análisis de datos

El pipeline de análisis está desarrollado principalmente con:

- Python
- Pandas
- NumPy
- scikit-learn
- pyodbc
- SQL Server
- Jupyter / Google Colab

El proceso contempla las fases principales de KDD:

1. **Extracción:** obtención incremental de datos desde la base operativa.
2. **Limpieza:** eliminación de duplicados, tratamiento de nulos, validación de coordenadas y corrección de inconsistencias.
3. **Transformación:** zonificación, clasificación de eventos y cálculo de indicadores.
4. **Minería de datos:** clasificación mediante Decision Tree.
5. **Carga:** almacenamiento de los resultados en el esquema analítico.

## 📍 DBSCAN

DBSCAN se utiliza para detectar zonas de riesgo a partir de las coordenadas geográficas de los eventos.

Parámetros utilizados:

```text
eps = 12 metros
min_samples = 3
métrica = haversine
```

Ventajas:

- No requiere conocer previamente el número de zonas.
- Detecta eventos aislados como ruido.
- Trabaja con proximidad geográfica real.

El conjunto optimizado permitió identificar **10 zonas de riesgo**, con **0 eventos clasificados como ruido** y **0 zonas espurias**.

---

# 📐 Índice de Accesibilidad por Zona (IAZ)

El IAZ es la métrica central del diagnóstico.

```text
IAZ = Σ peso de severidad de eventos
      ───────────────────────────────
       recorridos que cruzaron la zona
```

Pesos:

| Severidad | Peso |
| --------- | ---: |
| Baja      |    1 |
| Media     |    3 |
| Crítica   |    5 |

Clasificación:

|           IAZ | Accesibilidad |
| ------------: | ------------- |
|         `< 3` | Alta          |
| `3 ≤ IAZ < 6` | Media         |
|         `≥ 6` | Baja          |

El uso de umbrales fijos permite mantener un criterio consistente entre diferentes instituciones.

---

# 🤖 Modelo de clasificación

Se implementó un `DecisionTreeClassifier` de scikit-learn utilizando variables de sensores como fuerza de impacto, distancia y sensores infrarrojos.

El modelo obtuvo una exactitud de **96.67 %** sobre el conjunto de prueba.

> Este modelo está aislado del diagnóstico real de Vision Guard y se implementó como parte del componente académico de minería de datos. El diagnóstico operativo utiliza principalmente DBSCAN e IAZ.

---

# 📊 Resultados

Los principales resultados del análisis fueron:

- **10 zonas de riesgo** identificadas mediante DBSCAN.
- **0 eventos clasificados como ruido**.
- **0 zonas espurias**.
- **6 puntos de riesgo** verificados físicamente utilizados para validar los resultados.
- Coincidencia del tipo de evento predominante con el riesgo esperado en los puntos reales.
- **96.67 % de exactitud** en el modelo Decision Tree.
- IAZ promedio inicial de **8.21** sobre las zonas evaluadas.

Los resultados permiten identificar y priorizar zonas que requieren mayor atención desde una perspectiva de accesibilidad.

---

# ⚠️ Limitaciones

Vision Guard tiene un alcance exclusivamente **descriptivo y diagnóstico**.

El sistema:

- No realiza navegación autónoma.
- No genera certificaciones normativas.
- No pretende sustituir una evaluación humana.
- No utiliza modelos predictivos para generar el diagnóstico.
- Depende de la cantidad y calidad de los recorridos registrados.

El IAZ puede ser sensible a un número reducido de recorridos. Por ello, resultados basados en muestras pequeñas deben interpretarse con cautela y no necesariamente como ausencia de riesgo.

---

# 🚀 Trabajo futuro

- Incrementar la cantidad de recorridos.
- Ampliar la cobertura de zonas.
- Incorporar nuevos sensores.
- Mejorar la detección de incidencias.
- Incorporar nuevos indicadores de accesibilidad.
- Ampliar las visualizaciones del dashboard.
- Evaluar modelos predictivos como posible evolución futura.
- Permitir análisis comparativos entre diferentes instituciones o campus.

---

# ⚙️ Tecnologías

| Área             | Tecnologías                      |
| ---------------- | -------------------------------- |
| IoT              | ESP32, MicroPython, MQTT, WiFi   |
| Sensores         | HC-SR04, MPU6050, IR, GPS NEO-6M |
| Móvil            | Kotlin, Android                  |
| Backend          | ASP.NET Core, .NET, C#           |
| Frontend         | Angular, TypeScript              |
| Visualización    | Chart.js, Leaflet, leaflet.heat  |
| Cartografía      | OpenStreetMap                    |
| ETL              | Python, Pandas, NumPy, pyodbc    |
| Machine Learning | scikit-learn, Decision Tree      |
| Clustering       | DBSCAN                           |
| Base de datos    | Microsoft SQL Server             |
| Análisis         | Jupyter / Google Colab           |

---

# ▶️ Ejecución

## Backend

```bash
dotnet restore
dotnet build
dotnet run
```

## ETL

Abrir:

```text
etl_visionguard_v2.ipynb
```

Instalar dependencias:

```bash
pip install pandas numpy scikit-learn pyodbc
```

Configurar las credenciales de SQL Server mediante variables de entorno o configuración local.

## Dashboard

```bash
npm install
ng serve
```

## Aplicación móvil

Abrir el proyecto en Android Studio y ejecutar en un dispositivo físico o emulador compatible.

## Firmware

Configurar las credenciales de red y parámetros del dispositivo y cargar el firmware correspondiente en el ESP32.

---

# 👥 Equipo

| Integrante                            | Responsabilidad                         |
| ------------------------------------- | --------------------------------------- |
| Aideé Vanessa Casillas Tapia          | Firmware ESP32, integración IoT y MQTT  |
| Diego Jair Borja Romero               | Backend y servicios                     |
| Antonio Damián Rodiguez Alarcon       | ETL, Data Warehouse y análisis de datos |
| Danna Guadalupe Federica Rios Buendia | Portal web                              |
| Arleth Naomi Moran Hernández          | Landing web/UX UI                       |

---

# 📚 Referencias

- Angular — https://angular.dev/
- Chart.js — https://www.chartjs.org/docs/latest/
- Leaflet — https://leafletjs.com/reference.html
- Leaflet.heat — https://github.com/Leaflet/Leaflet.heat
- Microsoft SQL Server — https://learn.microsoft.com/sql/
- Pandas — https://pandas.pydata.org/docs/
- Python — https://docs.python.org/3/
- Matplotlib — https://matplotlib.org/stable/
- McKinney, W. (2022). _Python for Data Analysis_. O'Reilly Media.
- Han, J., Kamber, M., & Pei, J. (2012). _Data Mining: Concepts and Techniques_ (3rd ed.). Morgan Kaufmann.

---

## 📄 Licencia

Proyecto desarrollado con fines académicos como parte del proyecto integrador de noveno cuatrimestre de la Universidad Tecnológica de León. Periodo escolar Mayo-Agosto 2026.
