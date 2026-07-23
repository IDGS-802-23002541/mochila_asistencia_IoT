# 📋 ESPECIFICACIÓN DE ENDPOINTS Y PAYLOADS PARA EL ESP32

## Contexto Arquitectónico
- **Modelo:** Batch Processing (sin tiempo real)
- **Inicialización:** App móvil genera `RecorridoId` y lo envía vía Bluetooth al ESP32
- **Transmisión:** El ESP32 guarda datos localmente y transmite todo al finalizar por HTTP o MQTT
- **Puertos Restringidos:** Solo 80 (HTTP) y 443 (HTTPS/WebSocket)

---

## 1️⃣ INICIALIZACIÓN (App Móvil → Backend)

### Endpoint
```
POST /api/recorridos/iniciar
Content-Type: application/json
```

### Request Body
```json
{
  "dispositivoMac": "24:0A:C4:8B:58:FC",
  "usuarioEdad": 35,
  "discapacidadId": 2
}
```

### Response (HTTP 200 OK)
```json
{
  "recorridoId": 123,
  "dispositivoMac": "24:0A:C4:8B:58:FC",
  "fechaInicio": "2025-06-25T14:30:00Z",
  "mensaje": "Recorrido iniciado correctamente"
}
```

**⚠️ Acción:** El móvil transmite `RecorridoId=123` al ESP32 vía Bluetooth. El ESP32 lo guarda localmente.

---

## 2️⃣ RECORRIDO (ESP32 → Backend)

### Opción A: HTTP (Recomendado si MQTT no está disponible)

#### Endpoint
```
POST /api/telemetria/finalizar
Content-Type: application/json
```

#### Request Body
```json
{
  "macAddress": "24:0A:C4:8B:58:FC",
  "recorridoId": 123,
  "fechaFin": "2025-06-25T15:45:00Z",
  "rutaCoordenadas": [
    {
      "lat": 21.1645,
      "lon": -101.6789,
      "ts": "2025-06-25T14:31:00Z"
    },
    {
      "lat": 21.1646,
      "lon": -101.6790,
      "ts": "2025-06-25T14:32:00Z"
    }
  ],
  "usuarioEdad": 35,
  "discapacidadId": 2,
  "eventos": [
    {
      "tipoEventoId": 1,
      "timestampEvento": "2025-06-25T15:00:00Z",
      "latitud": 21.1650,
      "longitud": -101.6800,
      "geoEsEstimado": false,
      "fuerzaImpactoG": 4.5
    },
    {
      "tipoEventoId": 2,
      "timestampEvento": "2025-06-25T15:20:00Z",
      "latitud": 21.1660,
      "longitud": -101.6810,
      "geoEsEstimado": true,
      "fuerzaImpactoG": null
    }
  ]
}
```

#### Response (HTTP 200 OK)
```json
{
  "recorridoId": 123,
  "fechaFin": "2025-06-25T15:45:00Z",
  "totalEventos": 2,
  "mensaje": "Recorrido finalizado y guardado correctamente"
}
```

---

### Opción B: MQTT (Si tienes broker disponible)

**Configuración:**
- **Host:** `localhost` o tu broker public
- **Puerto:** `443` (WebSocket WSS)
- **Topics:**
  - `cangurera/eventos` — cada evento detectado
  - `cangurera/recorrido/finalizar` — cierre del recorrido

#### Topic: `cangurera/eventos`
```json
{
  "recorridoId": 123,
  "tipoEventoId": 1,
  "latitud": 21.1650,
  "longitud": -101.6800,
  "geoEsEstimado": false,
  "fuerzaImpactoG": 4.5
}
```

#### Topic: `cangurera/recorrido/finalizar`
```json
{
  "recorridoId": 123,
  "rutaCoordenadas": "[{\"lat\":21.1645,\"lon\":-101.6789,\"ts\":\"2025-06-25T14:31:00Z\"}]",
  "fechaFin": "2025-06-25T15:45:00Z"
}
```

---

## 3️⃣ ESPECIFICACIONES DEL FIRMWARE (ESP32)

### Flujo de Datos

```
┌─────────────────────────────────────────────────────────────┐
│  1. App móvil hace POST /api/recorridos/iniciar             │
│     ↓ Recibe RecorridoId = 123                              │
│     ↓ Envía RecorridoId al ESP32 vía Bluetooth              │
│                                                              │
│  2. ESP32 guarda RecorridoId localmente en memoria/SPIFFS   │
│     ↓ Inicia sensores: GPS, acelerómetro, ultrasónico       │
│     ↓ Cada evento anómalo se guarda en buffer local         │
│                                                              │
│  3. Mientras tanto:                                          │
│     - GPS (NEO-6M): Captura lat/lon cada N segundos         │
│     - MPU6050: Detecta aceleración anómala (caídas)         │
│     - HC-SR04: Detecta obstáculos                           │
│     ↓ Todos los eventos se asocian a RecorridoId            │
│                                                              │
│  4. Al finalizar (botón o evento de devolución):            │
│     ↓ ESP32 construye JSON de ruta (array de coord)         │
│     ↓ ESP32 construye array de eventos con timestamps       │
│     ↓ POST a /api/telemetria/finalizar con payload completo │
│     ↓ Backend valida, guarda y responde OK                  │
└─────────────────────────────────────────────────────────────┘
```

---

## 4️⃣ DETALLE DE CAMPOS Y VALIDACIONES

### MacAddress
- **Formato:** `XX:XX:XX:XX:XX:XX` (hexadecimal)
- **Ejemplo:** `24:0A:C4:8B:58:FC`
- **Validación:** Regex en backend: `^([0-9A-Fa-f]{2}:){5}[0-9A-Fa-f]{2}$`

### RecorridoId
- **Tipo:** `int` positivo
- **Origen:** Generado por app móvil (Database Auto-increment)
- **Rango:** 1 ≤ RecorridoId < 2,147,483,647
- **Obligatorio:** Sí

### RutaCoordenadas / rutaCoordenadas
- **Formato:** Array JSON de objetos con lat/lon/timestamp
- **Schema esperado:**
  ```json
  [
    {
      "lat": 21.1645,      // DECIMAL(10,8)
      "lon": -101.6789,    // DECIMAL(10,8)
      "ts": "2025-06-25T14:31:00Z"  // ISO 8601 UTC
    }
  ]
  ```
- **Restricción SQL:** `ISJSON(Ruta_Coordenadas) = 1`
- **Validación Backend:** Intenta `JsonDocument.Parse()`; si falla, rechaza con HTTP 400

### Eventos
- **Array de objetos con:**
  - `tipoEventoId` (int): Referencia a `Cat_TiposEvento`
  - `timestampEvento` (DateTime UTC): Si no viene, backend asume `DateTime.UtcNow`
  - `latitud` (decimal?): `DECIMAL(10,8)` en SQL
  - `longitud` (decimal?): `DECIMAL(10,8)` en SQL
  - `geoEsEstimado` (bool): `true` si GPS sin fix en interiores, `false` si coordenadas precisas
  - `fuerzaImpactoG` (decimal?): `DECIMAL(5,2)` en SQL, solo para eventos de caída

---

## 5️⃣ CATÁLOGO DE TIPOS DE EVENTO

Insertar en `Operativo.Cat_TiposEvento`:

| Id  | NombreEvento        | Severidad |
|-----|---------------------|-----------|
| 1   | Caída               | Alta      |
| 2   | Tráfico Denso       | Media     |
| 3   | Obstáculo           | Baja      |
| 4   | Cambio de Elevación | Baja      |
| 5   | GPS Sin Señal       | Baja      |

---

## 6️⃣ CATÁLOGO DE DISCAPACIDADES

Insertar en `Operativo.Cat_TiposDiscapacidad`:

| Id  | Nombre          |
|-----|-----------------|
| 1   | Ceguera Total   |
| 2   | Baja Visión     |
| 3   | Daltonismo      |
| 4   | Sordera         |
| 5   | Movilidad       |

---

## 7️⃣ FLUJO DE ERROR Y REINTENTOS

### Casos de Error HTTP
| Código | Causa | Acción ESP32 |
|--------|-------|-------------|
| 400 | JSON inválido, campos faltantes | Reintentar con validación local |
| 401 | MacAddress no coincide | Verificar MAC hardcoded |
| 404 | RecorridoId no existe o ya está cerrado | Abortar, log de error |
| 500 | Error servidor | Reintentar en 30-60s (máx 3 intentos) |

### Reintento Recomendado
```
Intento 1: Inmediato
Intento 2: 30 segundos después
Intento 3: 60 segundos después
Si todos fallan: Guardar datos en SPIFFS para sincronización manual posterior
```

---

## 8️⃣ NOTAS IMPORTANTES

1. **GPS en Interiores:** Marcar `geoEsEstimado = true` si el GPS no tiene fix (no actualiza durante N segundos)
2. **RecorridoId Inmutable:** El ESP32 debe guardar el RecorridoId exactamente como lo recibe del móvil
3. **Timestamps en UTC:** Todos los `TimestampEvento`, `FechaFin`, etc., deben ser en UTC (zona horaria Z)
4. **MacAddress Única:** La validación rechaza dispositivos con MAC no registrada en `Operativo.Dispositivos`
5. **Batch Processing:** No hay reporte en tiempo real. Todo se transmite al finalizar el recorrido.

---

## 9️⃣ EJEMPLO COMPLETO DE RECORRIDO

### 1. App móvil (Moment 0)
```bash
curl -X POST http://localhost:5000/api/recorridos/iniciar \
  -H "Content-Type: application/json" \
  -d '{
    "dispositivoMac": "24:0A:C4:8B:58:FC",
    "usuarioEdad": 35,
    "discapacidadId": 2
  }'
```
**Respuesta:** `RecorridoId = 1234`

### 2. ESP32 (Moment 0 → Moment T)
- Guarda `RecorridoId = 1234` en memoria
- Detecta 3 eventos de caída en coordenadas (lat, lon)
- Graba 150 puntos GPS durante 75 minutos
- Finalmente:

```bash
curl -X POST http://localhost:5000/api/telemetria/finalizar \
  -H "Content-Type: application/json" \
  -d '{
    "macAddress": "24:0A:C4:8B:58:FC",
    "recorridoId": 1234,
    "fechaFin": "2025-06-25T15:45:00Z",
    "rutaCoordenadas": [
      {"lat": 21.1645, "lon": -101.6789, "ts": "2025-06-25T14:31:00Z"},
      ...150 puntos más...
    ],
    "eventos": [
      {"tipoEventoId": 1, "timestampEvento": "2025-06-25T14:45:00Z", "latitud": 21.165, "longitud": -101.679, "geoEsEstimado": false, "fuerzaImpactoG": 5.2},
      {"tipoEventoId": 1, "timestampEvento": "2025-06-25T15:00:00Z", "latitud": 21.170, "longitud": -101.680, "geoEsEstimado": true, "fuerzaImpactoG": 3.8},
      {"tipoEventoId": 2, "timestampEvento": "2025-06-25T15:20:00Z", "latitud": 21.175, "longitud": -101.685, "geoEsEstimado": true, "fuerzaImpactoG": null}
    ]
  }'
```

**Respuesta:** HTTP 200
```json
{
  "recorridoId": 1234,
  "fechaFin": "2025-06-25T15:45:00Z",
  "totalEventos": 3,
  "mensaje": "Recorrido finalizado y guardado correctamente"
}
```

---

## 🔟 CONEXIÓN EN HTTPS/WSS (Producción)

Para usar puertos 443 (HTTPS) en **producción:**

1. El backend expone HTTPS en puerto 443
2. El firmware ESP32 conecta a `wss://api.example.com:443/mqtt` (WebSocket Secure)
3. El backend valida certificados SSL/TLS

**Config appsettings.json:**
```json
{
  "Mqtt": {
    "Host": "api.example.com",
    "Port": 443,
    "UseWebSocket": true,
    "UseTls": true
  }
}
```

---

## 📞 CONTACTO & PREGUNTAS

- **Backend:** Diego (Puertos 80/443, EF Core, SQL Server)
- **Firmware:** Tu compañero (ESP32, Bluetooth, sensores)
- **App Móvil:** [Asignado a]

Cualquier duda sobre formato de payload o campos, consulta este documento.
