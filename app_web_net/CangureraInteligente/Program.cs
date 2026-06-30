using CangureraInteligente.Data;
using CangureraInteligente.Services;
using Microsoft.EntityFrameworkCore;

var builder = WebApplication.CreateBuilder(args);

// ── Base de datos ──────────────────────────────────────────────────────────
builder.Services.AddDbContext<CangureraDbContext>(opts =>
    opts.UseSqlServer(builder.Configuration.GetConnectionString("CangureraDB")));

// ── MQTT ───────────────────────────────────────────────────────────────────
// Soportar ambas variantes de sección en appsettings: "MQTT" y "Mqtt"
var mqttSettings = builder.Configuration
    .GetSection("MQTT")
    .Get<MqttSettings>()
    ?? builder.Configuration.GetSection("Mqtt").Get<MqttSettings>()
    ?? new MqttSettings();

builder.Services.AddSingleton(mqttSettings);
builder.Services.AddScoped<IMqttTelemetryProcessor, MqttTelemetryProcessor>();
builder.Services.AddHostedService<MqttListenerService>();
builder.Services.AddSingleton<MqttConnectionManager>();
builder.Services.AddSingleton<IMqttPublisherService, MqttPublisherService>();
builder.Services.AddSingleton<ZonaCalienteAlertState>();
// ── Controllers / Swagger ──────────────────────────────────────────────────
builder.Services.AddControllers();
builder.Services.AddEndpointsApiExplorer();
builder.Services.AddSwaggerGen(c =>
{
    c.SwaggerDoc("v1", new()
    {
        Title       = "Cangurera Inteligente API",
        Version     = "v1",
        Description = "API para el sistema de préstamo de mochila asistiva. " +
                      "HTTP para la app móvil, MQTT para el ESP32."
    });
    // Incluir comentarios XML en Swagger
    var xmlFile = $"{System.Reflection.Assembly.GetExecutingAssembly().GetName().Name}.xml";
    var xmlPath = Path.Combine(AppContext.BaseDirectory, xmlFile);
    if (File.Exists(xmlPath)) c.IncludeXmlComments(xmlPath);
});

// ── CORS (opcional, útil durante desarrollo móvil) ─────────────────────────
builder.Services.AddCors(o => o.AddDefaultPolicy(p =>
    p.AllowAnyOrigin().AllowAnyHeader().AllowAnyMethod()));

var app = builder.Build();

// ── Middleware ─────────────────────────────────────────────────────────────
if (app.Environment.IsDevelopment())
{
    app.UseSwagger();
    app.UseSwaggerUI();
}

app.UseCors();
app.MapControllers();

app.Run();