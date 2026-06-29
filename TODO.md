# TODO - Migración MQTT -> HTTP

## Paso 1: Inspección adicional
- [x] Revisar Program.cs
- [x] Revisar MqttListenerService
- [x] Revisar MqttTelemetryProcessor e interfaz
- [ ] Identificar DTO/payload exacto (MqttTelemetryPayload) para el endpoint HTTP

## Paso 2: Implementación HTTP
- [ ] Crear `Controllers/TelemetriaController.cs` con `POST /api/telemetria`
- [ ] Conectar controller con el processor existente (reutilizar lógica)

## Paso 3: Eliminación MQTT
- [ ] Quitar `MQTTnet` del csproj
- [ ] Eliminar registro de hosted service/background
- [ ] Eliminar `MqttListenerService` (archivo y clases asociadas)
- [ ] Eliminar lectura/config de `Mqtt` en appsettings

## Paso 4: Refactor de nombres (opcional pero recomendado)
- [ ] Renombrar `IMqttTelemetryProcessor` -> `ITelemetryProcessor`
- [ ] Renombrar `MqttTelemetryProcessor` -> `TelemetryProcessor`

## Paso 5: Compilación y pruebas
- [ ] `dotnet build`
- [ ] Probar endpoint con curl/Postman

