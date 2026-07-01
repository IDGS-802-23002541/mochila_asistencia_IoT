package edu.utleon.idgs902.app_movil_android.Controllers

import android.content.Context
import android.content.Intent
import android.content.SharedPreferences
import android.os.Bundle
import android.os.Handler
import android.os.Looper
import android.util.Log
import android.widget.Button
import android.widget.TextView
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import com.google.android.material.bottomnavigation.BottomNavigationView
import edu.utleon.idgs902.app_movil_android.R
import edu.utleon.idgs902.app_movil_android.Models.RutaModels
import edu.utleon.idgs902.app_movil_android.Utils.HistorialHelper
import edu.utleon.idgs902.app_movil_android.Utils.VisionGuardBleManager
import org.json.JSONObject
import java.io.OutputStreamWriter
import java.net.HttpURLConnection
import java.net.URL
import java.text.SimpleDateFormat
import java.util.Date
import java.util.Locale
import kotlin.concurrent.thread

class HomeActivity : AppCompatActivity() {

    // Variables para el cronómetro (Modificadas para persistencia)
    private var corriendo = false
    private val handler = Handler(Looper.getMainLooper())
    private lateinit var sharedPreferences: SharedPreferences
    private lateinit var globalPreferences: SharedPreferences

    // Componentes visuales
    private lateinit var txtTiempo: TextView
    private lateinit var btnIniciarRecorrido: Button
    private lateinit var btnDetalles: Button

    // Gestor Bluetooth para mandar START/STOP
    private lateinit var bleManager: VisionGuardBleManager

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
        globalPreferences = getSharedPreferences("VisionGuardPrefs", Context.MODE_PRIVATE)

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

        // Inicializar el Bluetooth en segundo plano para mandar los comandos seriales
        bleManager = VisionGuardBleManager(this, object : VisionGuardBleManager.BleStateListener {
            override fun onConectado() {
                Log.d("HomeActivity", "Mochila enlazada por Bluetooth en segundo plano.")
            }

            override fun onDesconectado() {
                Log.d("HomeActivity", "Mochila desconectada.")
            }

            override fun onDispositivoEncontrado(nombre: String, mac: String) {}

            override fun onError(mensaje: String) {
                Log.e("HomeActivity", "Error BLE: $mensaje")
            }
        })

        // Conectar automáticamente a la mochila enlazada anteriormente
        val macMochila = globalPreferences.getString("dispositivo_mac", null)
        if (!macMochila.isNullOrEmpty()) {
            bleManager.conectar(macMochila)
        }

        // Verificar si ya había un recorrido activo al entrar/abrir de nuevo la app
        corriendo = sharedPreferences.getBoolean("cronometro_corriendo", false)
        if (corriendo) {
            btnIniciarRecorrido.text = "Detener"
            btnIniciarRecorrido.setTextColor(resources.getColor(android.R.color.holo_red_dark, theme))
            btnIniciarRecorrido.setBackgroundResource(R.drawable.bg_button_outline_red)
            handler.post(runnableCronometro)
        }

        btnIniciarRecorrido.setOnClickListener {
            if (!corriendo) {
                if (macMochila.isNullOrEmpty()) {
                    Toast.makeText(this, "Por favor vincula la mochila por Bluetooth primero.", Toast.LENGTH_LONG).show()
                    val intent = Intent(this, DevicesActivity::class.java)
                    startActivity(intent)
                } else {
                    iniciarRecorridoServidor(macMochila)
                }
            } else {
                detenerRecorridoLocal()
            }
        }

        // Navegación directa hacia la pantalla de Monitoreo / Detalles
        btnDetalles.setOnClickListener {
            val intent = Intent(this, MonitoreoActivity::class.java)
            startActivity(intent)
        }
    }

    /**
     * Paso A: Petición HTTP POST al backend de Diego para iniciar el viaje y generar el RecorridoId
     */
    private fun iniciarRecorridoServidor(macAddress: String) {
        thread {
            try {
                // Endpoint proporcionado por Diego
                val url = URL("http://34.30.116.129/api/recorridos/iniciar")
                val conn = url.openConnection() as HttpURLConnection
                conn.requestMethod = "POST"
                conn.setRequestProperty("Content-Type", "application/json; utf-8")
                conn.doOutput = true

                // Body del Payload
                val jsonInputString = JSONObject().apply {
                    put("dispositivoMac", macAddress)
                    put("usuarioEdad", 35)      // Datos demográficos de prueba
                    put("discapacidadId", 2)    // Baja visión
                }.toString()

                conn.outputStream.use { os ->
                    val writer = OutputStreamWriter(os, "UTF-8")
                    writer.write(jsonInputString)
                    writer.flush()
                }

                val code = conn.responseCode
                if (code == HttpURLConnection.HTTP_OK || code == HttpURLConnection.HTTP_CREATED) {
                    val respuesta = conn.inputStream.bufferedReader().use { it.readText() }
                    val jsonResponse = JSONObject(respuesta)
                    val recorridoId = jsonResponse.getInt("recorridoId")

                    // Volvemos al hilo principal para actualizar las UI e iniciar Bluetooth
                    runOnUiThread {
                        iniciarRecorridoLocal(recorridoId)
                    }
                } else {
                    runOnUiThread {
                        Toast.makeText(this, "Error de red con el servidor de HiverMQTT: $code", Toast.LENGTH_LONG).show()
                    }
                }
            } catch (e: Exception) {
                Log.e("HomeActivity", "Fallo HTTP", e)
                runOnUiThread {
                    Toast.makeText(this, "No se pudo contactar al Backend. Iniciando offline.", Toast.LENGTH_LONG).show()
                    // Si el backend falla, iniciamos offline con un ID simulado
                    iniciarRecorridoLocal((System.currentTimeMillis() % 100000).toInt())
                }
            }
        }
    }

    /**
     * Paso B: Mandar comando por Bluetooth e iniciar interfaz de cronómetro
     */
    private fun iniciarRecorridoLocal(recorridoId: Int) {
        corriendo = true
        sharedPreferences.edit().apply {
            putLong("tiempo_inicio", System.currentTimeMillis())
            putBoolean("cronometro_corriendo", true)
            putInt("ultimo_recorrido_id", recorridoId)
            apply()
        }
        handler.post(runnableCronometro)

        // Enviar el comando serial "START:<ID>" por Bluetooth al ESP32
        bleManager.enviarInicioRecorrido(recorridoId)

        establecerVistaDetener()
        Toast.makeText(this, "¡Recorrido #$recorridoId iniciado!", Toast.LENGTH_SHORT).show()
    }

    private fun detenerRecorridoLocal() {
        // Enviar señal "STOP" por Bluetooth para que la mochila envíe su batch JSON a HiveMQTT
        bleManager.enviarDetenerRecorrido()

        val tiempoFinal = txtTiempo.text.toString()
        val sdf = SimpleDateFormat("dd 'de' MMMM", Locale("es", "MX"))
        val fechaHoy = sdf.format(Date())

        val idRecorrido = sharedPreferences.getInt("ultimo_recorrido_id", 0)

        val nuevaRuta = RutaModels(
            id = idRecorrido.toString(),
            fecha = fechaHoy,
            duracion = tiempoFinal,
            obstaculos = "0", // Se actualizarán mediante el broker
            caidas = "0",
            eventos = "0",
            distancia = "0"
        )

        HistorialHelper.guardarRuta(this, nuevaRuta)

        corriendo = false
        handler.removeCallbacks(runnableCronometro)
        sharedPreferences.edit().apply {
            putLong("tiempo_inicio", 0L)
            putBoolean("cronometro_corriendo", false)
            apply()
        }

        establecerVistaIniciar()
        txtTiempo.text = "00:00"

        val intent = Intent(this, MonitoreoActivity::class.java).apply {
            putExtra("EXTRA_DURACION", nuevaRuta.duracion)
        }
        startActivity(intent)
    }

    private fun establecerVistaDetener() {
        btnIniciarRecorrido.text = "Detener"
        btnIniciarRecorrido.setTextColor(resources.getColor(android.R.color.holo_red_dark, theme))
        btnIniciarRecorrido.setBackgroundResource(R.drawable.bg_button_outline_red)
    }

    private fun establecerVistaIniciar() {
        btnIniciarRecorrido.text = "Iniciar recorrido"
        btnIniciarRecorrido.setTextColor(resources.getColor(R.color.vg_dark_blue, theme))
        btnIniciarRecorrido.setBackgroundResource(R.drawable.bg_button_outline_blue)
    }

    override fun onResume() {
        super.onResume()
        // Cuando regresas a la app, si está corriendo, reactivamos de inmediato el bucle visual
        corriendo = sharedPreferences.getBoolean("cronometro_corriendo", false)
        if (corriendo) {
            handler.post(runnableCronometro)
        }
        // Reconectar por si acaso
        val macMochila = globalPreferences.getString("dispositivo_mac", null)
        if (!macMochila.isNullOrEmpty()) {
            bleManager.conectar(macMochila)
        }
    }

    override fun onPause() {
        super.onPause()
        // Evita fugas de memoria si la app pasa a segundo plano deteniendo el bucle visual,
        // pero la marca de tiempo sigue segura en el almacenamiento.
        handler.removeCallbacks(runnableCronometro)
    }

    override fun onDestroy() {
        super.onDestroy()
        bleManager.desconectar()
    }
}