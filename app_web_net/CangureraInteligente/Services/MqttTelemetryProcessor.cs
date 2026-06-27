using System.Text.Json;
using CangureraInteligente.DTOs;
using Microsoft.Extensions.DependencyInjection;

namespace CangureraInteligente.Services;

/// <summary>
/// Implementación por defecto del procesador de telemetría.
/// Intenta resolver un servicio de dominio conocido (p. ej. `IRecorridoService`) y delegar.
/// Si no existe una implementación concreta, registra el mensaje y devuelve true para evitar reintentos infinitos.
/// </summary>
public class MqttTelemetryProcessor : IMqttTelemetryProcessor
{
    private readonly IServiceProvider _provider;
    private readonly ILogger<MqttTelemetryProcessor> _log;

    public MqttTelemetryProcessor(IServiceProvider provider, ILogger<MqttTelemetryProcessor> log)
    {
        _provider = provider;
        _log = log;
    }

    public async Task<bool> ProcessAsync(MqttTelemetryPayload payload, CancellationToken ct = default)
    {
        _log.LogInformation("Procesando telemetría: dispositivo={Id} lat={Lat} lon={Lon} bat={Bat} vel={Vel} ts={Ts}",
            payload.DispositivoId, payload.Latitud, payload.Longitud, payload.Bateria, payload.Velocidad, payload.Fecha);

        // Intenta delegar a un servicio de dominio existente si está registrado.
        // Ejemplo esperado (opcional) de servicio: IRecorridoService o ITelemetriaService.
        try
        {
            using var scope = _provider.CreateScope();
            var sp = scope.ServiceProvider;

            // Intentar resolver dinámicamente un servicio de dominio por nombre
            var telemInterface = AppDomain.CurrentDomain.GetAssemblies()
                .SelectMany(a => a.GetTypes())
                .FirstOrDefault(t => t.IsInterface && (t.Name == "ITelemetriaService" || t.Name == "IRecorridoService"));

            if (telemInterface is not null)
            {
                var telemSvc = sp.GetService(telemInterface);
                if (telemSvc is not null)
                {
                    var method = telemSvc.GetType().GetMethod("HandleTelemetryAsync")
                              ?? telemSvc.GetType().GetMethod("ProcessTelemetryAsync");
                    if (method is not null)
                    {
                        var task = (Task)method.Invoke(telemSvc, new object[] { payload, ct })!;
                        await task.ConfigureAwait(false);
                        return true;
                    }
                }
            }

            // No se encontró servicio específico; registrar payload en debug y continuar.
            _log.LogDebug("No se encontró servicio de dominio para telemetría; payload: {Payload}", JsonSerializer.Serialize(payload));
            return true;
        }
        catch (Exception ex)
        {
            _log.LogError(ex, "Error al procesar telemetría MQTT");
            return false;
        }
    }
}
