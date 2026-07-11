using System;
using System.IO;
using System.Reflection;
using CangureraInteligente.Data;
using CangureraInteligente.Models;
using CangureraInteligente.Services;
using Microsoft.AspNetCore.Builder;
using Microsoft.AspNetCore.Hosting;
using Microsoft.EntityFrameworkCore;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Hosting;
using Microsoft.OpenApi.Models;

var builder = WebApplication.CreateBuilder(args);

builder.WebHost.UseUrls(builder.Configuration["ASPNETCORE_URLS"] ?? "http://0.0.0.0:5151");

builder.Services.AddDbContext<CangureraDbContext>(opts =>
    opts.UseSqlServer(builder.Configuration.GetConnectionString("CangureraDB")));

var mqttSettings = builder.Configuration.GetSection("MQTT").Get<MqttSettings>()
    ?? builder.Configuration.GetSection("Mqtt").Get<MqttSettings>()
    ?? new MqttSettings();

builder.Services.AddSingleton(mqttSettings);
builder.Services.AddScoped<IMqttTelemetryProcessor, MqttTelemetryProcessor>();
builder.Services.AddHostedService<MqttListenerService>();
builder.Services.AddSingleton<MqttConnectionManager>();
builder.Services.AddSingleton<IMqttPublisherService, MqttPublisherService>();
builder.Services.AddSingleton<ZonaCalienteAlertState>();
builder.Services.AddControllers();
builder.Services.AddEndpointsApiExplorer();
builder.Services.AddSwaggerGen(c =>
{
    c.SwaggerDoc("v1", new OpenApiInfo
    {
        Title = "Cangurera Inteligente API",
        Version = "v1",
        Description = "API para el sistema de préstamo de mochila asistiva. HTTP para la app móvil, MQTT para el ESP32."
    });

    var xmlPath = Path.Combine(AppContext.BaseDirectory, Assembly.GetExecutingAssembly().GetName().Name + ".xml");
    if (File.Exists(xmlPath))
    {
        c.IncludeXmlComments(xmlPath);
    }
});
builder.Services.AddCors(options =>
{
    options.AddDefaultPolicy(policy =>
        policy.AllowAnyOrigin()
            .AllowAnyHeader()
            .AllowAnyMethod());
});

var app = builder.Build();

if (app.Environment.IsDevelopment())
{
    app.UseSwagger();
    app.UseSwaggerUI();
}

app.UseCors();
app.MapControllers();
app.Run();