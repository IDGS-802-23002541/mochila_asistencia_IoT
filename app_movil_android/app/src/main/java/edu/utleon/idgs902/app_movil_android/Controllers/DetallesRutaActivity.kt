package edu.utleon.idgs902.app_movil_android.Controllers

import android.os.Bundle
import android.widget.LinearLayout
import android.widget.TextView
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import androidx.recyclerview.widget.RecyclerView
import edu.utleon.idgs902.app_movil_android.R
import edu.utleon.idgs902.app_movil_android.Utils.RecorridoDetalleResponse
import edu.utleon.idgs902.app_movil_android.Utils.ResumenRecorridoResponse
import edu.utleon.idgs902.app_movil_android.Utils.VisionGuardApiService
import retrofit2.Call
import retrofit2.Callback
import retrofit2.Response

class DetallesRutaActivity : AppCompatActivity() {

    private lateinit var apiService: VisionGuardApiService

    // Identificadores exactos de tu XML
    private lateinit var lblTituloVentana: TextView
    private lateinit var btnRegresar: LinearLayout
    private lateinit var lblDetalleFecha: TextView
    private lateinit var lblDetalleDuracion: TextView
    private lateinit var lblDetalleDistancia: TextView
    private lateinit var lblDetalleEventos: TextView
    private lateinit var rvEventosInternos: RecyclerView

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_detalles_ruta) // Vinculado a tu XML

        apiService = VisionGuardApiService.create()

        // Enlace de componentes con los ID exactos que pusiste en tu XML
        lblTituloVentana = findViewById(R.id.lblTituloVentana)
        btnRegresar = findViewById(R.id.btnRegresar)
        lblDetalleFecha = findViewById(R.id.lblDetalleFecha)
        lblDetalleDuracion = findViewById(R.id.lblDetalleDuracion)
        lblDetalleDistancia = findViewById(R.id.lblDetalleDistancia)
        lblDetalleEventos = findViewById(R.id.lblDetalleEventos)
        rvEventosInternos = findViewById(R.id.rvEventosInternos)

        // Configurar comportamiento del botón regresar
        btnRegresar.setOnClickListener {
            finish()
        }

        // Pintamos el título inicial enviado por el Adapter (Ej: "Ruta #1")
        val titulo = intent.getStringExtra("NUMERO_RUTA") ?: "Detalle de Ruta"
        lblTituloVentana.text = titulo

        // Recuperamos el ID que manda el Adapter para consumirlo de la API de tu compañero
        val recorridoId = intent.getStringExtra("RECORRIDO_ID")?.toIntOrNull() ?: -1

        if (recorridoId != -1) {
            consultarDatosServidor(recorridoId)
        } else {
            // Datos de respaldo por si no viene un ID de red
            lblDetalleFecha.text = intent.getStringExtra("FECHA") ?: "---"
            lblDetalleDuracion.text = intent.getStringExtra("DURACION") ?: "00:00"
            lblDetalleDistancia.text = intent.getStringExtra("DISTANCIA") ?: "0 m"
            lblDetalleEventos.text = intent.getStringExtra("CANTIDAD_EVENTOS") ?: "0"
        }
    }

    private fun consultarDatosServidor(id: Int) {
        // Petición 1: Detalle para ver cuántos eventos se registraron
        apiService.obtenerDetalleRecorrido(id).enqueue(object : Callback<RecorridoDetalleResponse> {
            override fun onResponse(call: Call<RecorridoDetalleResponse>, response: Response<RecorridoDetalleResponse>) {
                if (response.isSuccessful && response.body() != null) {
                    val detalle = response.body()!!

                    // Petición 2: Resumen para obtener las distancias y tiempos de la ruta
                    apiService.obtenerResumenRecorrido(id).enqueue(object : Callback<ResumenRecorridoResponse> {
                        override fun onResponse(call: Call<ResumenRecorridoResponse>, resumenResponse: Response<ResumenRecorridoResponse>) {
                            if (resumenResponse.isSuccessful && resumenResponse.body() != null) {
                                val resumen = resumenResponse.body()!!

                                // 1. Pintar cantidad de Eventos reales de la API
                                lblDetalleEventos.text = detalle.totalEventos.toString()

                                // 2. Formatear y pintar Fecha limpia (ej: de "2026-07-02T10:00:00Z" a "2026-07-02")
                                lblDetalleFecha.text = detalle.fechaInicio.split("T").firstOrNull() ?: detalle.fechaInicio

                                // 3. Formatear y pintar Distancia en m o km
                                lblDetalleDistancia.text = if (resumen.distanciaTotalMetros >= 1000) {
                                    String.format("%.2f km", resumen.distanciaTotalMetros / 1000)
                                } else {
                                    String.format("%.0f m", resumen.distanciaTotalMetros)
                                }
                                // 4. Formatear y pintar Duración en minutos
                                val minutos = (resumen.duracionSegundos ?: 0.0) / 60.0
                                lblDetalleDuracion.text = String.format("%.1f min", minutos)

                                // Opcional: Aquí puedes configurar el LayoutManager y Adaptador
                                // de tu rvEventosInternos para mostrar la bitácora si fuera necesario.
                            }
                        }

                        override fun onFailure(call: Call<ResumenRecorridoResponse>, t: Throwable) {
                            Toast.makeText(this@DetallesRutaActivity, "Error en resumen de ruta", Toast.LENGTH_SHORT).show()
                        }
                    })
                }
            }

            override fun onFailure(call: Call<RecorridoDetalleResponse>, t: Throwable) {
                Toast.makeText(this@DetallesRutaActivity, "Error de comunicación con servidor", Toast.LENGTH_SHORT).show()
            }
        })
    }
}