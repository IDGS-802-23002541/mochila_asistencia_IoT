package edu.utleon.idgs902.app_movil_android.Controllers

import android.content.Context
import android.content.Intent
import android.content.SharedPreferences
import android.os.Bundle
import android.os.Handler
import android.os.Looper
import android.widget.Button
import android.widget.TextView
import androidx.appcompat.app.AppCompatActivity
import com.google.android.material.bottomnavigation.BottomNavigationView
import edu.utleon.idgs902.app_movil_android.R
import edu.utleon.idgs902.app_movil_android.Models.RutaModels
import edu.utleon.idgs902.app_movil_android.Utils.HistorialHelper
import java.text.SimpleDateFormat
import java.util.Date
import java.util.Locale

class HomeActivity : AppCompatActivity() {

    // Variables para el cronómetro (Modificadas para persistencia)
    private var corriendo = false
    private val handler = Handler(Looper.getMainLooper())
    private lateinit var sharedPreferences: SharedPreferences

    // Componentes visuales
    private lateinit var txtTiempo: TextView
    private lateinit var btnIniciarRecorrido: Button
    private lateinit var btnDetalles: Button

    private val runnableCronometro = object : Runnable {
        override fun run() {
            if (corriendo) {
                // Obtener el tiempo de inicio guardado
                val tiempoInicio = sharedPreferences.getLong("tiempo_inicio", 0L)
                if (tiempoInicio != 0L) {
                    // Calcular la diferencia real con la hora actual
                    val diferenciaMilis = System.currentTimeMillis() - tiempoInicio
                    val segundosTotales = (diferenciaMilis / 1000).toInt()

                    val minutosVisuales = segundosTotales / 60
                    val segundosVisuales = segundosTotales % 60

                    // Formato 00:00
                    txtTiempo.text = String.format("%02d:%02d", minutosVisuales, segundosVisuales)
                }
                // Vuelve a ejecutar este bloque en 1 segundo
                handler.postDelayed(this, 1000)
            }
        }
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_home)

        // Inicializar almacenamiento interno para persistir el estado del cronómetro
        sharedPreferences = getSharedPreferences("CronometroPrefs", Context.MODE_PRIVATE)

        val bottomNavigation = findViewById<BottomNavigationView>(R.id.bottomNavigation)
        bottomNavigation.selectedItemId = R.id.nav_home

        bottomNavigation.setOnItemSelectedListener { item ->
            when (item.itemId) {
                R.id.nav_home -> {
                    true
                }
                R.id.nav_historial -> {
                    // Redireccionar a la pantalla de Historial
                    val intent = Intent(this, HistorialActivity::class.java)
                    startActivity(intent)
                    overridePendingTransition(0, 0)
                    finish()
                    true
                }
                else -> false
            }
        }

        // Enlazar componentes del XML
        txtTiempo = findViewById(R.id.txtTiempo)
        btnIniciarRecorrido = findViewById(R.id.btnIniciarRecorrido)
        btnDetalles = findViewById(R.id.btnDetallesHome)

        // Verificar si ya había un recorrido activo al entrar/abrir de nuevo la app
        corriendo = sharedPreferences.getBoolean("cronometro_corriendo", false)
        if (corriendo) {
            btnIniciarRecorrido.text = "Detener"
            btnIniciarRecorrido.setTextColor(resources.getColor(android.R.color.holo_red_dark, theme))
            btnIniciarRecorrido.setBackgroundResource(R.drawable.bg_button_outline_red)
            handler.post(runnableCronometro)
        }

        // Lógica del botón Iniciar / Detener recorrido
        btnIniciarRecorrido.setOnClickListener {
            if (!corriendo) {
                // Iniciar el recorrido guardando la marca de tiempo exacta del sistema
                corriendo = true
                sharedPreferences.edit().apply {
                    putLong("tiempo_inicio", System.currentTimeMillis())
                    putBoolean("cronometro_corriendo", true)
                    apply()
                }
                handler.post(runnableCronometro)

                // Cambios visuales basados en tu diseño de referencia
                btnIniciarRecorrido.text = "Detener"
                btnIniciarRecorrido.setTextColor(resources.getColor(android.R.color.holo_red_dark, theme))
                btnIniciarRecorrido.setBackgroundResource(R.drawable.bg_button_outline_red)
            } else {
                // 1. Capturar los datos de la duración antes de limpiar el cronómetro
                val tiempoFinal = txtTiempo.text.toString()

                // Obtener fecha actual formateada de manera automática
                val sdf = SimpleDateFormat("dd 'de' MMMM", Locale("es", "MX"))
                val fechaHoy = sdf.format(Date())

                // 2. Crear el objeto RutaModels
                // Nota: Los contadores inician en "0" provisionalmente; se actualizarán mediante tu base de datos
                val nuevaRuta = RutaModels(
                    id = System.currentTimeMillis().toString(),
                    fecha = fechaHoy,
                    duracion = tiempoFinal,
                    obstaculos = "0",
                    caidas = "0",
                    eventos = "0",
                    distancia = "0"
                )

                // 3. Registrar en el historial local de SharedPreferences
                HistorialHelper.guardarRuta(this, nuevaRuta)

                // 4. Detener el recorrido y limpiar la memoria interna del cronómetro
                corriendo = false
                handler.removeCallbacks(runnableCronometro)
                sharedPreferences.edit().apply {
                    putLong("tiempo_inicio", 0L)
                    putBoolean("cronometro_corriendo", false)
                    apply()
                }

                // Cambios visuales del botón
                btnIniciarRecorrido.text = "Iniciar recorrido"
                btnIniciarRecorrido.setTextColor(resources.getColor(R.color.vg_dark_blue, theme))
                btnIniciarRecorrido.setBackgroundResource(R.drawable.bg_button_outline_blue)
                txtTiempo.text = "00:00"

                // 5. Redireccionar enviando únicamente la duración medida por el teléfono
                val intent = Intent(this, MonitoreoActivity::class.java).apply {
                    putExtra("EXTRA_DURACION", nuevaRuta.duracion)
                }
                startActivity(intent)
            }
        }

        // Navegación directa hacia la pantalla de Monitoreo / Detalles
        btnDetalles.setOnClickListener {
            val intent = Intent(this, MonitoreoActivity::class.java)
            startActivity(intent)
        }
    }

    override fun onResume() {
        super.onResume()
        // Cuando regresas a la app, si está corriendo, reactivamos de inmediato el bucle visual
        corriendo = sharedPreferences.getBoolean("cronometro_corriendo", false)
        if (corriendo) {
            handler.post(runnableCronometro)
        }
    }

    override fun onPause() {
        super.onPause()
        // Evita fugas de memoria si la app pasa a segundo plano deteniendo el bucle visual,
        // pero la marca de tiempo sigue segura en el almacenamiento.
        handler.removeCallbacks(runnableCronometro)
    }
}