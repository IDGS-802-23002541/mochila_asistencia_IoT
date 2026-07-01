package edu.utleon.idgs902.app_movil_android.Controllers

import android.Manifest
import android.content.Context
import android.content.Intent
import android.content.SharedPreferences
import android.content.pm.PackageManager
import android.os.Build
import android.os.Bundle
import android.widget.Button
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import androidx.core.app.ActivityCompat
import androidx.core.content.ContextCompat
import edu.utleon.idgs902.app_movil_android.R
import edu.utleon.idgs902.app_movil_android.Utils.VisionGuardBleManager

class DevicesActivity : AppCompatActivity() {

    private lateinit var bleManager: VisionGuardBleManager
    private lateinit var sharedPreferences: SharedPreferences
    private lateinit var btnVincular: Button

    companion object {
        private const val PERMISSION_REQUEST_CODE = 101
    }


    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_devices)

        sharedPreferences = getSharedPreferences("VisionGuardPrefs", Context.MODE_PRIVATE)
        btnVincular = findViewById(R.id.btnVincular)

        // Inicializar nuestro gestor de Bluetooth BLE
        bleManager = VisionGuardBleManager(this, object : VisionGuardBleManager.BleStateListener {
            override fun onConectado() {
                Toast.makeText(this@DevicesActivity, "¡Mochila Conectada con Éxito!", Toast.LENGTH_SHORT).show()
                // Una vez conectados de forma física, pasamos a la pantalla de Verificación
                val intent = Intent(this@DevicesActivity, VerificationActivity::class.java)
                startActivity(intent)
            }

            override fun onDesconectado() {
                btnVincular.text = "Vincular dispositivo"
                btnVincular.isEnabled = true
            }

            override fun onDispositivoEncontrado(nombre: String, mac: String) {
                // Guardar la dirección MAC para auto-conexión futura
                sharedPreferences.edit().putString("dispositivo_mac", mac).apply()
                // Conectar al ESP32 por su dirección de hardware
                bleManager.conectar(mac)
            }

            override fun onError(mensaje: String) {
                Toast.makeText(this@DevicesActivity, mensaje, Toast.LENGTH_LONG).show()
                btnVincular.text = "Vincular dispositivo"
                btnVincular.isEnabled = true
            }
        })

        // Programar la lógica del botón de vinculación con permisos
        btnVincular.setOnClickListener {
            if (verificarPermisosBluetooth()) {
                iniciarConexionMochila()
            } else {
                solicitarPermisosBluetooth()
            }
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
            arrayOf(
                Manifest.permission.BLUETOOTH_SCAN,
                Manifest.permission.BLUETOOTH_CONNECT
            )
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
    private fun setupListInteractions() {
        //back
    }
}