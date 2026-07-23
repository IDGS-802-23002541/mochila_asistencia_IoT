package edu.utleon.idgs902.app_movil_android.Utils

import retrofit2.Call
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory
import retrofit2.http.Body
import retrofit2.http.GET
import retrofit2.http.POST
import retrofit2.http.Path
import retrofit2.http.Query

// Login
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

// Dispositivos
data class DispositivoResponse(
    val id: Int,
    val organizacionId: Int,
    val macAddress: String,
    val estado: String,
    val ultimaConexion: String?,
    val fechaRegistro: String?,
    val organizacion: String
)

// Recorridos
data class RecorridoDetalleResponse(
    val id: Int,
    val dispositivoMac: String,
    val organizacion: String? = null,
    val fechaInicio: String,
    val fechaFin: String? = null,
    val usuarioEdad: Int? = null,
    val discapacidad: String? = null,
    val activo: Boolean = true,
    val totalEventos: Int
)

data class RecorridoHistorialResponse(
    val id: Int,
    val dispositivoMac: String,
    val fechaInicio: String,
    val fechaFin: String?,
    val duracionSegundos: Double,
    val totalEventos: Int,
    val distanciaTotalMetros: Double
)

data class ResumenRecorridoResponse(
    val recorridoId: Int? = null,
    val totalPuntos: Int = 0,
    val distanciaTotalMetros: Double,
    val duracionSegundos: Double? = null,
    val velocidadPromedioKmh: Double? = null,
    val coordenadas: List<CoordenadaResponse> = emptyList()
)

data class CoordenadaResponse(
    val latitud: Double? = null,
    val longitud: Double? = null,
    val timestamp: String? = null,
    val lat: Double? = null,
    val lon: Double? = null,
    val ts: String? = null
)

interface VisionGuardApiService {

    @POST("usuarios/login")
    fun login(@Body request: LoginRequest): Call<LoginResponse>

    @GET("dispositivos")
    fun obtenerDispositivos(@Query("organizacionId") organizacionId: Int): Call<List<DispositivoResponse>>

    @GET("recorridos/{id}")
    fun obtenerDetalleRecorrido(@Path("id") recorridoId: Int): Call<RecorridoDetalleResponse>

    @GET("recorridos")
    fun obtenerHistorialPorOrganizacion(@Query("organizacionId") organizacionId: Int): Call<List<RecorridoHistorialResponse>>

    @GET("recorridos/dispositivo/{mac}")
    fun obtenerHistorialPorDispositivo(@Path("mac") mac: String): Call<List<RecorridoHistorialResponse>>

    @GET("recorridos/{id}/resumen")
    fun obtenerResumenRecorrido(@Path("id") recorridoId: Int): Call<ResumenRecorridoResponse>

    companion object {
        private const val BASE_URL = "https://lmsidgs902.runasp.net/api/"

        fun create(): VisionGuardApiService {
            val retrofit = Retrofit.Builder()
                .baseUrl(BASE_URL)
                .addConverterFactory(GsonConverterFactory.create())
                .build()
            return retrofit.create(VisionGuardApiService::class.java)
        }
    }
}