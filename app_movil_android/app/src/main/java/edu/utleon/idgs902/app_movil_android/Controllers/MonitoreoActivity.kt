package edu.utleon.idgs902.app_movil_android.Controllers

import android.content.Context
import android.content.Intent
import android.content.SharedPreferences
import android.os.Bundle
import android.widget.Button
import android.widget.TextView
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import edu.utleon.idgs902.app_movil_android.Utils.EventoRecorridoResponse
import edu.utleon.idgs902.app_movil_android.Utils.RecorridoDetalleResponse
import edu.utleon.idgs902.app_movil_android.Utils.ResumenRecorridoResponse
import edu.utleon.idgs902.app_movil_android.Utils.VisionGuardApiService
import edu.utleon.idgs902.app_movil_android.R
import edu.utleon.idgs902.app_movil_android.Utils.MqttConfig
import edu.utleon.idgs902.app_movil_android.Utils.MqttHolder
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

        btnDesvincular.setOnClickListener {
            val mac = sharedPreferences.getString("dispositivo_mac", "") ?: ""

            if (mac.isNotEmpty()) {
                val jsonDesvincular = JSONObject().apply {
                    put("accion", "desvincular")
                    put("macAddress", mac)
                }

                mqtt?.publicar(
                    MqttConfig.TOPICO_COMANDOS,
                    jsonDesvincular.toString()
                )
            }

            Toast.makeText(this, "Dispositivo desvinculado con éxito", Toast.LENGTH_SHORT).show()

            val intent = Intent(this, DevicesActivity::class.java).apply {
                flags = Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_CLEAR_TASK
            }
            startActivity(intent)
            finish()
        }
    }

    private fun cargarInformacionDeRuta(
        id: Int,
        txtTiempo: TextView,
        txtObstaculos: TextView,
        txtCaidas: TextView,
        txtEventos: TextView
    ) {
        // 1. Cargar Tiempo desde el endpoint de Resumen
        apiService.obtenerResumenRecorrido(id).enqueue(object : Callback<ResumenRecorridoResponse> {
            override fun onResponse(call: Call<ResumenRecorridoResponse>, response: Response<ResumenRecorridoResponse>) {
                if (response.isSuccessful && response.body() != null) {
                    val resumen = response.body()!!
                    val minutosTotales = (resumen.duracionSegundos ?: 0.0) / 60.0
                    txtTiempo.text = String.format("%.1f min", minutosTotales)
                } else {
                    txtTiempo.text = "0.0 min"
                }
            }

            override fun onFailure(call: Call<ResumenRecorridoResponse>, t: Throwable) {
                txtTiempo.text = "0.0 min"
            }
        })

        // 2. Cargar Lista de Eventos y clasificar (Obstáculos vs Caídas)
        apiService.obtenerEventosRecorrido(id).enqueue(object : Callback<List<EventoRecorridoResponse>> {
            override fun onResponse(call: Call<List<EventoRecorridoResponse>>, response: Response<List<EventoRecorridoResponse>>) {
                if (response.isSuccessful && response.body() != null) {
                    val listaEventos = response.body()!!

                    var numCaidas = 0
                    var numObstaculos = 0

                    for (evento in listaEventos) {
                        val tipo = evento.tipo.lowercase()
                        if (tipo.contains("caida") || tipo.contains("caída")) {
                            numCaidas++
                        } else {
                            numObstaculos++
                        }
                    }

                    txtEventos.text = listaEventos.size.toString()
                    txtObstaculos.text = numObstaculos.toString()
                    txtCaidas.text = numCaidas.toString()
                } else {
                    txtEventos.text = "0"
                    txtObstaculos.text = "0"
                    txtCaidas.text = "0"
                }
            }

            override fun onFailure(call: Call<List<EventoRecorridoResponse>>, t: Throwable) {
                Toast.makeText(this@MonitoreoActivity, "Error al obtener eventos del recorrido", Toast.LENGTH_SHORT).show()
                txtEventos.text = "0"
                txtObstaculos.text = "0"
                txtCaidas.text = "0"
            }
        })
    }
}