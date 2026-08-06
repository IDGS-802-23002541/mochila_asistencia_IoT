package edu.utleon.idgs902.app_movil_android.Models

import java.util.Date
data class RutaModels(
    val id: String,
    val fecha: String,
    val fechaRaw: Date? = null,   // NUEVO: fecha real para poder filtrar por rango
    val duracion: String,
    val obstaculos: String,
    val caidas: String,
    val eventos: String,
    val distancia: String
)