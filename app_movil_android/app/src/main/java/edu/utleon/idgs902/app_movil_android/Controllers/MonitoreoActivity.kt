package edu.utleon.idgs902.app_movil_android.Controllers

import android.os.Bundle
import android.widget.TextView
import androidx.appcompat.app.AppCompatActivity
import edu.utleon.idgs902.app_movil_android.R

class MonitoreoActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_monitoreo)

        // Enlazar los TextViews de tus 4 cajitas del diseño
        val txtTiempo = findViewById<TextView>(R.id.txtTiempoDetalle)
        val txtObstaculos = findViewById<TextView>(R.id.txtObstaculosDetalle)
        val txtCaidas = findViewById<TextView>(R.id.txtCaidasDetalle)
        val txtEventos = findViewById<TextView>(R.id.txtEventosDetalle)

        // Recibir los datos enviados por la pantalla anterior
        val duracion = intent.getStringExtra("EXTRA_DURACION") ?: "00:00"
        val obstaculos = intent.getStringExtra("EXTRA_OBSTACULOS") ?: "0"
        val caidas = intent.getStringExtra("EXTRA_CAIDAS") ?: "0"
        val eventos = intent.getStringExtra("EXTRA_EVENTOS") ?: "0"

        // Asignarlos a las tarjetas visuales
        txtTiempo.text = duracion
        txtObstaculos.text = obstaculos
        txtCaidas.text = caidas
        txtEventos.text = eventos

        // Botón regresar
        findViewById<TextView>(R.id.btnRegresar).setOnClickListener {
            finish()
        }
    }
}