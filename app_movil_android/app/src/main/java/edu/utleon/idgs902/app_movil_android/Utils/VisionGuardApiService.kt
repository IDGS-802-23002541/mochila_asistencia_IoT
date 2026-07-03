package edu.utleon.idgs902.app_movil_android.Utils

import retrofit2.Call
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory
import retrofit2.http.GET
import retrofit2.http.Path

// 1. Estructura para GET /api/recorridos/{id}
data class RecorridoDetalleResponse(
    val id: Int,
    val dispositivoMac: String,
    val fechaInicio: String,
    val totalEventos: Int
)

// 2. Estructura para GET /api/recorridos/{id}/resumen
data class ResumenRecorridoResponse(
    val recorridoId: Int,
    val distanciaTotalMetros: Double,
    val duracionSegundos: Int,
    val coordenadas: List<CoordenadaResponse>
)

data class CoordenadaResponse(
    val lat: Double,
    val lon: Double,
    val ts: String
)

// 3. Interfaz de Retrofit
interface VisionGuardApiService {

    @GET("recorridos/{id}")
    fun obtenerDetalleRecorrido(
        @Path("id") recorridoId: Int
    ): Call<RecorridoDetalleResponse>

    @GET("recorridos/{id}/resumen")
    fun obtenerResumenRecorrido(
        @Path("id") recorridoId: Int
    ): Call<ResumenRecorridoResponse>

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