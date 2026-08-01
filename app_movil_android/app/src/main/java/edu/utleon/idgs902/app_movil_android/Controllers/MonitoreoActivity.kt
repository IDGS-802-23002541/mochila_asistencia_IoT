package edu.utleon.idgs902.app_movil_android.Controllers

import android.content.Context
import android.content.Intent
import android.content.SharedPreferences
import android.os.Bundle
import android.widget.Button
import android.widget.TextView
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import edu.utleon.idgs902.app_movil_android.Utils.RecorridoDetalleResponse
import edu.utleon.idgs902.app_movil_android.Utils.ResumenRecorridoResponse
import edu.utleon.idgs902.app_movil_android.Utils.VisionGuardApiService
import edu.utleon.idgs902.app_movil_android.R
import edu.utleon.idgs902.app_movil_android.Utils.MqttConfig
import edu.utleon.idgs902.app_movil_android.Utils.MqttHolder
import edu.utleon.idgs902.app_movil_android.Utils.MqttManager
import org.json.JSONObject
import retrofit2.Call
import retrofit2.Callback
import retrofit2.Response

class MonitoreoActivity : AppCompatActivity() {

    private lateinit var apiService: VisionGuardApiService
    private lateinit var sharedPreferences: SharedPreferences

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_monitoreo)

        // Inicializar SharedPreferences (Asegúrate de usar el mismo nombre "VisionGuardPrefs")
        sharedPreferences = getSharedPreferences("VisionGuardPrefs", Context.MODE_PRIVATE)
        apiService = VisionGuardApiService.create()
        val mqtt = MqttHolder.mqttManager

        val txtTiempo = findViewById<TextView>(R.id.txtTiempoDetalle)
        val txtObstaculos = findViewById<TextView>(R.id.txtObstaculosDetalle)
        val txtCaidas = findViewById<TextView>(R.id.txtCaidasDetalle)
        val txtEventos = findViewById<TextView>(R.id.txtEventosDetalle)
        val btnDesvincular = findViewById<Button>(R.id.btnDesvincular)

        var recorridoId = intent.getIntExtra("RECORRIDO_ID", -1)
        if (recorridoId == -1) {
            recorridoId = intent.getStringExtra("RECORRIDO_ID")?.toIntOrNull() ?: -1
        }

        if (recorridoId != -1) {
            txtTiempo.text = "..."
            txtObstaculos.text = "..."
            txtCaidas.text = "..."
            txtEventos.text = "..."
            cargarInformacionDeRuta(recorridoId, txtTiempo, txtObstaculos, txtCaidas, txtEventos)
        } else {
            txtTiempo.text = intent.getStringExtra("EXTRA_DURACION") ?: "00:00"
            txtObstaculos.text = intent.getStringExtra("EXTRA_OBSTACULOS") ?: "0"
            txtCaidas.text = intent.getStringExtra("EXTRA_CAIDAS") ?: "0"
            txtEventos.text = intent.getStringExtra("EXTRA_EVENTOS") ?: "0"
        }

        findViewById<TextView>(R.id.btnRegresar).setOnClickListener {
            finish()
        }

        // 🛠️ LOGICA ACTUALIZADA DE DESVINCULACIÓN
        btnDesvincular.setOnClickListener {
            val mac = sharedPreferences.getString("dispositivo_mac", "") ?: ""

            if (mac.isNotEmpty()) {

                val jsonDesvincular  = JSONObject().apply{
                    put("accion", "desvincular")
                    put("macAddress", mac)
                }

                mqtt?.publicar(
                    MqttConfig.TOPICO_COMANDOS,
                    jsonDesvincular.toString()
                )
            }

            Toast.makeText(this, "Dispositivo desvinculado con éxito", Toast.LENGTH_SHORT).show()

            // 2. Crear el Intent para ir a DevicesActivity
            val intent = Intent(this, DevicesActivity::class.java).apply {
                // Estas banderas limpian todo el historial de ventanas de atrás
                // para evitar que el usuario regrese al monitoreo con el botón físico de Android
                flags = Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_CLEAR_TASK
            }
            startActivity(intent)
            finish() // Cierra la pantalla actual
        }
    }

    private fun cargarInformacionDeRuta(
        id: Int,
        txtTiempo: TextView,
        txtObstaculos: TextView,
        txtCaidas: TextView,
        txtEventos: TextView
    ) {
        apiService.obtenerDetalleRecorrido(id).enqueue(object : Callback<RecorridoDetalleResponse> {
            override fun onResponse(call: Call<RecorridoDetalleResponse>, response: Response<RecorridoDetalleResponse>) {
                if (response.isSuccessful && response.body() != null) {
                    val detalle = response.body()!!

                    apiService.obtenerResumenRecorrido(id).enqueue(object : Callback<ResumenRecorridoResponse> {
                        override fun onResponse(call: Call<ResumenRecorridoResponse>, resumenResponse: Response<ResumenRecorridoResponse>) {
                            if (resumenResponse.isSuccessful && resumenResponse.body() != null) {
                                val resumen = resumenResponse.body()!!
                                txtEventos.text = detalle.totalEventos.toString()
                                val minutosTotales = (resumen.duracionSegundos ?: 0.0) / 60.0
                                txtTiempo.text = String.format("%.1f min", minutosTotales)
                                txtObstaculos.text = detalle.totalEventos.toString()
                                txtCaidas.text = "0"
                            }
                        }

                        override fun onFailure(call: Call<ResumenRecorridoResponse>, t: Throwable) {
                            Toast.makeText(this@MonitoreoActivity, "Error al calcular tiempos", Toast.LENGTH_SHORT).show()
                        }
                    })
                }
            }

            override fun onFailure(call: Call<RecorridoDetalleResponse>, t: Throwable) {
                Toast.makeText(this@MonitoreoActivity, "Fallo al conectar con el servidor", Toast.LENGTH_SHORT).show()
            }
        })
    }
}