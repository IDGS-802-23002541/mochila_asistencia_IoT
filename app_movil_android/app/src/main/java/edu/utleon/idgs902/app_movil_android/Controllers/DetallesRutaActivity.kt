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

import androidx.recyclerview.widget.LinearLayoutManager
import edu.utleon.idgs902.app_movil_android.Models.EventoRutaModels
import edu.utleon.idgs902.app_movil_android.Utils.CoordenadaResponse
import edu.utleon.idgs902.app_movil_android.Utils.EventoInternoAdapter
import edu.utleon.idgs902.app_movil_android.Utils.EventoRecorridoResponse
import java.text.SimpleDateFormat
import java.util.Locale

import org.osmdroid.config.Configuration
import org.osmdroid.tileprovider.tilesource.TileSourceFactory
import org.osmdroid.util.GeoPoint
import org.osmdroid.views.MapView
import org.osmdroid.views.overlay.Polyline

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

    private lateinit var mapaRecorrido: MapView

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        Configuration.getInstance().load(applicationContext, getSharedPreferences("osmdroid", MODE_PRIVATE))
        Configuration.getInstance().userAgentValue = packageName
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

        mapaRecorrido = findViewById(R.id.mapaRecorrido)
        mapaRecorrido.setTileSource(TileSourceFactory.MAPNIK)
        mapaRecorrido.setMultiTouchControls(true)

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
            cargarEventosDeRuta(recorridoId)
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

                                pintarRecorridoEnMapa(resumen.coordenadas)
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

    private fun cargarEventosDeRuta(id: Int) {
    apiService.obtenerEventosRecorrido(id).enqueue(object : Callback<List<EventoRecorridoResponse>> {
        override fun onResponse(
            call: Call<List<EventoRecorridoResponse>>,
            response: Response<List<EventoRecorridoResponse>>
        ) {
            if (response.isSuccessful && response.body() != null) {
                val eventosMapeados = response.body()!!.map { mapearAEventoRuta(it) }
                rvEventosInternos.layoutManager = LinearLayoutManager(this@DetallesRutaActivity)
                rvEventosInternos.adapter = EventoInternoAdapter(eventosMapeados)
            }
        }

        override fun onFailure(call: Call<List<EventoRecorridoResponse>>, t: Throwable) {
            // Silencioso por ahora: si falla, el bloque simplemente queda vacío
        }
    })
}

    private fun pintarRecorridoEnMapa(coordenadas: List<CoordenadaResponse>) {
        val puntos = coordenadas
            .filter { it.lat != null && it.lon != null }
            .map { GeoPoint(it.lat!!, it.lon!!) }

        android.util.Log.d("MapaDebug", "Coordenadas recibidas: ${coordenadas.size}, puntos válidos: ${puntos.size}, primer punto: ${puntos.firstOrNull()}")

        if (puntos.isEmpty()) return

        val polyline = Polyline().apply {
            setPoints(puntos)
            outlinePaint.color = android.graphics.Color.parseColor("#2563eb")
            outlinePaint.strokeWidth = 8f
        }

        mapaRecorrido.overlays.add(polyline)

        mapaRecorrido.post {
            val boundingBox = org.osmdroid.util.BoundingBox.fromGeoPoints(puntos)
            mapaRecorrido.zoomToBoundingBox(boundingBox, true, 100)
            mapaRecorrido.invalidate()
        }
    }


    private fun mapearAEventoRuta(e: EventoRecorridoResponse): EventoRutaModels {
        val color = when (e.severidad) {
            "Critica" -> "#8B2626"
            "Media" -> "#705315"
            else -> "#1E5631" // Baja
        }
        val hora = try {
            val parser = SimpleDateFormat("yyyy-MM-dd'T'HH:mm:ss", Locale.US)
            val sdf = SimpleDateFormat("hh:mm a", Locale.US)
            sdf.format(parser.parse(e.timestamp)!!)
        } catch (_: Exception) {
            e.timestamp
        }
        return EventoRutaModels(tipo = e.tipo, hora = hora, colorHex = color)
    }
    override fun onResume() {
        super.onResume()
        mapaRecorrido.onResume()
    }

    override fun onPause() {
        super.onPause()
        mapaRecorrido.onPause()
    }
}