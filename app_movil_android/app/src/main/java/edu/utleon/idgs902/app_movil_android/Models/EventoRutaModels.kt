package edu.utleon.idgs902.app_movil_android.Models

data class EventoRutaModels(
    val tipo: String,  // Ej: "Obstáculo detectado", "Proximidad alta", "Ruta finalizada"
    val hora: String,  // Ej: "10:12 am"
    val colorHex: String // Ej: "#8B2626" (Rojo), "#705315" (Café), "#1E5631" (Verde)
)