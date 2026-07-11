package edu.utleon.idgs902.app_movil_android.Controllers

import android.content.Context
import android.content.Intent
import android.content.SharedPreferences
import android.graphics.Color
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

    private var corriendo = false
    private val handler = Handler(Looper.getMainLooper())
    private lateinit var sharedPreferences: SharedPreferences
    private lateinit var globalPreferences: SharedPreferences

    // Componentes visuales
    private lateinit var txtTiempo: TextView
    private lateinit var btnIniciarRecorrido: Button
    private lateinit var btnDetalles: Button
    private lateinit var btnDetalles2: Button

    // Componentes de la tarjeta dinámica
    private lateinit var lblNombreMochilaHome: TextView
    private lateinit var lblStatusSenalHome: TextView
    private lateinit var lblBadgeStatusTexto: TextView
    private lateinit var badgeStatusContainer: android.view.View

    private lateinit var bleManager: VisionGuardBleManager

    private val runnableCronometro = object : Runnable {
        override fun run() {
            if (corriendo) {
                val tiempoInicio = sharedPreferences.getLong("tiempo_inicio", 0L)
                if (tiempoInicio != 0L) {
                    val diferenciaMilis = System.currentTimeMillis() - tiempoInicio
                    val segundosTotales = (diferenciaMilis / 1000).toInt()
                    val minutosVisuales = segundosTotales / 60
                    val segundosVisuales = segundosTotales % 60
                    txtTiempo.text = String.format("%02d:%02d", minutosVisuales, segundosVisuales)
                }
                handler.postDelayed(this, 1000)
            }
        }
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_home)

        sharedPreferences = getSharedPreferences("CronometroPrefs", Context.MODE_PRIVATE)
        globalPreferences = getSharedPreferences("VisionGuardPrefs", Context.MODE_PRIVATE)

        val bottomNavigation = findViewById<BottomNavigationView>(R.id.bottomNavigation)
        bottomNavigation.selectedItemId = R.id.nav_home

        bottomNavigation.setOnItemSelectedListener { item ->
            when (item.itemId) {
                R.id.nav_home -> true
                R.id.nav_historial -> {
                    val intent = Intent(this, HistorialActivity::class.java)
                    startActivity(intent)
                    overridePendingTransition(0, 0)
                    finish()
                    true
                }
                else -> false
            }
        }

        txtTiempo = findViewById(R.id.txtTiempo)
        btnIniciarRecorrido = findViewById(R.id.btnIniciarRecorrido)
        btnDetalles = findViewById(R.id.btnDetallesHome)
        btnDetalles2 = findViewById(R.id.btnDetallesHome2)

        lblNombreMochilaHome = findViewById(R.id.lblNombreMochilaHome)
        lblStatusSenalHome = findViewById(R.id.lblStatusSenalHome)
        lblBadgeStatusTexto = findViewById(R.id.lblBadgeStatusTexto)
        badgeStatusContainer = findViewById(R.id.badgeStatusContainer)

        bleManager = VisionGuardBleManager(this, object : VisionGuardBleManager.BleStateListener {
            override fun onConectado() {
                Log.d("HomeActivity", "Mochila enlazada por Bluetooth.")
            }
            override fun onDesconectado() {
                Log.d("HomeActivity", "Mochila desconectada.")
            }
            override fun onDispositivoEncontrado(nombre: String, mac: String) {}
            override fun onError(mensaje: String) {
                Log.e("HomeActivity", "Error BLE: $mensaje")
            }
            override fun onAckRecibido(comando: String) {
                Log.d("HomeActivity", "ACK recibido: $comando")
            }
        })

        verificarEstatusDispositivo()

        corriendo = sharedPreferences.getBoolean("cronometro_corriendo", false)
        if (corriendo) {
            establecerVistaDetener()
            handler.post(runnableCronometro)
        }

        btnIniciarRecorrido.setOnClickListener {
            val dispositivoVinculado = globalPreferences.getBoolean("dispositivo_vinculado", false)
            val macMochila = globalPreferences.getString("dispositivo_mac", null)

            if (!corriendo) {
                if (!dispositivoVinculado || macMochila.isNullOrEmpty()) {
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

        val navegarDetalles = android.view.View.OnClickListener {
            val intent = Intent(this, MonitoreoActivity::class.java)
            startActivity(intent)
        }
        btnDetalles.setOnClickListener(navegarDetalles)
        btnDetalles2.setOnClickListener(navegarDetalles)
    }

    private fun verificarEstatusDispositivo() {
        val dispositivoVinculado = globalPreferences.getBoolean("dispositivo_vinculado", false)
        val macMochila = globalPreferences.getString("dispositivo_mac", null)

        if (dispositivoVinculado && !macMochila.isNullOrEmpty()) {
            lblNombreMochilaHome.text = "Mochila enlazada"
            lblStatusSenalHome.text = "📶 Señal buena"
            lblStatusSenalHome.setTextColor(Color.parseColor("#2E7D32"))
            lblBadgeStatusTexto.text = "● Conectado"
            lblBadgeStatusTexto.setTextColor(Color.parseColor("#2E7D32"))
            badgeStatusContainer.background.setTintList(null)
            bleManager.conectar(macMochila)
        } else {
            lblNombreMochilaHome.text = "Sin dispositivo"
            lblStatusSenalHome.text = "⚠ Requiere vinculación"
            lblStatusSenalHome.setTextColor(Color.parseColor("#C62828"))
            lblBadgeStatusTexto.text = "🚫 Off-line"
            lblBadgeStatusTexto.setTextColor(Color.parseColor("#C62828"))
            badgeStatusContainer.background.setTint(Color.parseColor("#FFEBEE"))
        }
    }

    private fun iniciarRecorridoServidor(macAddress: String) {
        thread {
            try {
                val url = URL("https://lmsidgs902.runasp.net/api/recorridos/iniciar")
                val conn = url.openConnection() as HttpURLConnection
                conn.requestMethod = "POST"
                conn.setRequestProperty("Content-Type", "application/json; utf-8")
                conn.doOutput = true

                val jsonInputString = JSONObject().apply {
                    put("dispositivoMac", macAddress)
                    put("usuarioEdad", 35)
                    put("discapacidadId", 2)
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
                    iniciarRecorridoLocal((System.currentTimeMillis() % 100000).toInt())
                }
            }
        }
    }

    private fun iniciarRecorridoLocal(recorridoId: Int) {
        corriendo = true
        sharedPreferences.edit().apply {
            putLong("tiempo_inicio", System.currentTimeMillis())
            putBoolean("cronometro_corriendo", true)
            putInt("ultimo_recorrido_id", recorridoId)
            apply()
        }
        handler.post(runnableCronometro)
        bleManager.enviarInicioRecorrido(recorridoId)
        establecerVistaDetener()
        Toast.makeText(this, "¡Recorrido #$recorridoId iniciado!", Toast.LENGTH_SHORT).show()
    }

    private fun detenerRecorridoLocal() {
        bleManager.enviarDetenerRecorrido()

        val idRecorrido = sharedPreferences.getInt("ultimo_recorrido_id", 0)

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
            putExtra("RECORRIDO_ID", idRecorrido)
            putExtra("EXTRA_DURACION", txtTiempo.text.toString())
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
        corriendo = sharedPreferences.getBoolean("cronometro_corriendo", false)
        if (corriendo) {
            handler.post(runnableCronometro)
        }
        verificarEstatusDispositivo()
    }

    override fun onPause() {
        super.onPause()
        handler.removeCallbacks(runnableCronometro)
    }

    override fun onDestroy() {
        super.onDestroy()
        bleManager.desconectar()
    }
}