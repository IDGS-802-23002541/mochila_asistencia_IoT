package edu.utleon.idgs902.app_movil_android.Controllers

import android.os.Bundle
import android.widget.LinearLayout
import android.widget.TextView
import androidx.appcompat.app.AppCompatActivity
import androidx.recyclerview.widget.LinearLayoutManager
import androidx.recyclerview.widget.RecyclerView
import edu.utleon.idgs902.app_movil_android.R
import edu.utleon.idgs902.app_movil_android.Models.EventoRutaModels
import edu.utleon.idgs902.app_movil_android.Utils.EventoInternoAdapter

class DetallesRutaActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_detalles_ruta)

        // 1. Enlazar componentes de la vista
        val btnRegresar = findViewById<LinearLayout>(R.id.btnRegresar)
        val lblTituloVentana = findViewById<TextView>(R.id.lblTituloVentana)
        val lblDetalleFecha = findViewById<TextView>(R.id.lblDetalleFecha)
        val lblDetalleDuracion = findViewById<TextView>(R.id.lblDetalleDuracion)
        val lblDetalleDistancia = findViewById<TextView>(R.id.lblDetalleDistancia)
        val lblDetalleEventos = findViewById<TextView>(R.id.lblDetalleEventos)
        val rvEventosInternos = findViewById<RecyclerView>(R.id.rvEventosInternos)

        // 2. Recibir variables dinámicas de la pantalla anterior
        val numeroRuta = intent.getStringExtra("NUMERO_RUTA") ?: "Detalles"
        val fecha = intent.getStringExtra("FECHA") ?: "--"
        val duracion = intent.getStringExtra("DURACION") ?: "--"
        val distancia = intent.getStringExtra("DISTANCIA") ?: "0.0 km"
        val eventos = intent.getStringExtra("CANTIDAD_EVENTOS") ?: "0"

        // 3. Pintar la información dinámica sobre la UI
        lblTituloVentana.text = numeroRuta
        lblDetalleFecha.text = fecha
        lblDetalleDuracion.text = duracion
        lblDetalleDistancia.text = distancia
        lblDetalleEventos.text = eventos

        // 4. Preparar el RecyclerView de Eventos internos con datos de prueba
        rvEventosInternos.layoutManager = LinearLayoutManager(this)

        // Cambia esta lista simulada en el futuro cuando consumas tu Base de Datos
        val listaSimuladaDeEventos = listOf(
            EventoRutaModels("Obstáculo detectado", "10:12 am", "#8B2626"), // Círculo Rojo
            EventoRutaModels("Proximidad alta", "10:18 am", "#705315"),    // Círculo Café
            EventoRutaModels("Ruta finalizada", "10:37 am", "#1E5631")     // Círculo Verde
        )

        // Instanciar y asignar el adaptador interno
        val adapterInterno = EventoInternoAdapter(listaSimuladaDeEventos)
        rvEventosInternos.adapter = adapterInterno

        // 5. Destruir ventana actual al pulsar regresar
        btnRegresar.setOnClickListener {
            finish()
        }
    }
}