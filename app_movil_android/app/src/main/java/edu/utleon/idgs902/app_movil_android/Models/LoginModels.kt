package edu.utleon.idgs902.app_movil_android.Models

data class LoginRequest(
    val correo: String,
    val contrasena: String
)

data class LoginResponse(
    val id: Int,
    val nombre: String,
    val correo: String,
    val rol: String,
    val organizacionId: Int,
    val estado_Activo: Boolean,
    val mensaje: String
)