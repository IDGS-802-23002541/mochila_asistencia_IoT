package edu.utleon.idgs902.app_movil_android.Controllers

import android.Manifest
import android.content.Context
import android.content.Intent
import android.content.SharedPreferences
import android.content.pm.PackageManager
import android.os.Build
import android.os.Bundle
import android.widget.Button
import android.widget.LinearLayout
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import androidx.core.app.ActivityCompat
import androidx.core.content.ContextCompat
import edu.utleon.idgs902.app_movil_android.R
import edu.utleon.idgs902.app_movil_android.Utils.MqttConfig
import edu.utleon.idgs902.app_movil_android.Utils.MqttManager
import edu.utleon.idgs902.app_movil_android.Utils.VisionGuardBleManager
import org.json.JSONObject
import android.os.Handler
import android.os.Looper

class DevicesActivity : AppCompatActivity() {

    private lateinit var bleManager: VisionGuardBleManager
    private lateinit var sharedPreferences: SharedPreferences
    private lateinit var btnVincular: Button
    private lateinit var btnContinuarSinVincular: Button

    private lateinit var itemMochila1: LinearLayout
    private lateinit var itemMochila2: LinearLayout
    private lateinit var mqttManager: MqttManager
    private var macEncontrada = ""


    companion object {
        private const val PERMISSION_REQUEST_CODE = 101
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_devices)

        sharedPreferences = getSharedPreferences("VisionGuardPrefs", Context.MODE_PRIVATE)
        btnVincular = findViewById(R.id.btnVincular)
        btnContinuarSinVincular = findViewById(R.id.btnContinuarSinVincular)

        itemMochila1 = findViewById(R.id.itemMochila1)
        itemMochila2 = findViewById(R.id.itemMochila2)

        mqttManager = MqttManager(this,object : MqttManager.MqttListener {

            override fun onConectado() {}

            override fun onDesconectado() {}

            override fun onError(mensaje: String) {}
        })

        bleManager = VisionGuardBleManager(this, object : VisionGuardBleManager.BleStateListener {
            override fun onConectado() {

                // Marcamos que el ESP32 está vinculado a la app
                sharedPreferences.edit()
                    .putBoolean("dispositivo_vinculado", true)
                    .apply()

                Toast.makeText(this@DevicesActivity, "¡Mochila Conectada con Éxito!", Toast.LENGTH_SHORT).show()

                mqttManager.conectar()

                val json = JSONObject().apply {
                    put("accion", "vincular")
                    put("macAddress", macEncontrada)
                }

                mqttManager.publicar(
                    MqttConfig.TOPICO_COMANDOS,
                    json.toString()
                )

                bleManager.desconectar()

                val intent = Intent(this@DevicesActivity, HomeActivity::class.java)
                intent.flags = Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_CLEAR_TASK
                startActivity(intent)
                finish()

            }

            override fun onDesconectado() {
                btnVincular.text = "Vincular dispositivo"
                btnVincular.isEnabled = true
                // Dejamos la conexión activa hasta desvincular la app
            }

            override fun onDispositivoEncontrado(nombre: String, mac: String) {
                macEncontrada = mac
                sharedPreferences.edit()
                    .putString("dispositivo_mac", mac)
                    .putString("dispositivo_nombre", nombre)
                    .apply()
                bleManager.detenerEscaneo()
                bleManager.conectar(mac)
            }

            override fun onError(mensaje: String) {
                Toast.makeText(this@DevicesActivity, mensaje, Toast.LENGTH_LONG).show()
                btnVincular.text = "Vincular dispositivo"
                btnVincular.isEnabled = true
            }

        })

        btnVincular.setOnClickListener {
            if (verificarPermisosBluetooth()) {
                iniciarConexionMochila()
            } else {
                solicitarPermisosBluetooth()
            }
        }

        btnContinuarSinVincular.setOnClickListener {
            //Quitamos las preferencias del BLE
            sharedPreferences.edit()
                .remove("dispositivo_mac")
                .remove("dispositivo_nombre")
                .putBoolean("dispositivo_vinculado", false)
                .apply()
            val intent = Intent(this@DevicesActivity, HomeActivity::class.java)
            intent.flags = Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_CLEAR_TASK
            startActivity(intent)
            finish()
        }

        setupListInteractions()
    }

    private fun iniciarConexionMochila() {
        btnVincular.text = "Buscando mochila..."
        btnVincular.isEnabled = false
        bleManager.iniciarEscaneo()
    }

    private fun verificarPermisosBluetooth(): Boolean {
        return if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.S) {
            ContextCompat.checkSelfPermission(this, Manifest.permission.BLUETOOTH_SCAN) == PackageManager.PERMISSION_GRANTED &&
                    ContextCompat.checkSelfPermission(this, Manifest.permission.BLUETOOTH_CONNECT) == PackageManager.PERMISSION_GRANTED
        } else {
            ContextCompat.checkSelfPermission(this, Manifest.permission.ACCESS_FINE_LOCATION) == PackageManager.PERMISSION_GRANTED
        }
    }

    private fun solicitarPermisosBluetooth() {
        val permisos = if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.S) {
            arrayOf(Manifest.permission.BLUETOOTH_SCAN, Manifest.permission.BLUETOOTH_CONNECT)
        } else {
            arrayOf(Manifest.permission.ACCESS_FINE_LOCATION)
        }
        ActivityCompat.requestPermissions(this, permisos, PERMISSION_REQUEST_CODE)
    }

    override fun onRequestPermissionsResult(requestCode: Int, permissions: Array<out String>, grantResults: IntArray) {
        super.onRequestPermissionsResult(requestCode, permissions, grantResults)
        if (requestCode == PERMISSION_REQUEST_CODE) {
            if (grantResults.isNotEmpty() && grantResults.all { it == PackageManager.PERMISSION_GRANTED }) {
                iniciarConexionMochila()
            } else {
                Toast.makeText(this, "Permisos denegados. No se puede conectar a la mochila.", Toast.LENGTH_LONG).show()
            }
        }
    }


    /**
     * 🛠️ Lógica visual modificada para usar fondos con bordes redondeados
     */
    private fun setupListInteractions() {
        itemMochila1.setOnClickListener {
            // Asigna el XML del recurso redondeado
            itemMochila1.setBackgroundResource(R.drawable.bg_item_device_selector)
            itemMochila2.setBackgroundColor(0) // Remueve el fondo por completo
        }

        itemMochila2.setOnClickListener {
            itemMochila2.setBackgroundResource(R.drawable.bg_item_device_selector)
            itemMochila1.setBackgroundColor(0) // Remueve el fondo por completo
        }
    }
}