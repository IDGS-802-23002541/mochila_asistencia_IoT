package edu.utleon.idgs902.app_movil_android

import android.content.Context
import android.content.Intent
import android.content.SharedPreferences
import android.os.Bundle
import android.widget.Button
import android.widget.EditText
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import edu.utleon.idgs902.app_movil_android.Controllers.DevicesActivity
import edu.utleon.idgs902.app_movil_android.Utils.DispositivoResponse
import edu.utleon.idgs902.app_movil_android.Utils.LoginRequest
import edu.utleon.idgs902.app_movil_android.Utils.LoginResponse
import edu.utleon.idgs902.app_movil_android.Utils.VisionGuardApiService
import retrofit2.Call
import retrofit2.Callback
import retrofit2.Response

class MainActivity : AppCompatActivity() {

    private lateinit var sharedPreferences: SharedPreferences
    private val apiService = VisionGuardApiService.create()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        sharedPreferences = getSharedPreferences("VisionGuardPrefs", Context.MODE_PRIVATE)

        val etUsuario = findViewById<EditText>(R.id.etUsuario)
        val etPassword = findViewById<EditText>(R.id.etPassword)
        val btnIniciarSesion = findViewById<Button>(R.id.btnIniciarSesion)

        btnIniciarSesion.setOnClickListener {

            // Simular sesión para pruebas
            sharedPreferences.edit()
                .putInt("usuario_id", 1)
                .putString("usuario_nombre", "Prueba")
                .putString("usuario_correo", "prueba@test.com")
                .putString("usuario_rol", "Administrador")
                .putInt("organizacion_id", 1)
                .putString("dispositivo_mac", "00:11:22:33:44:55")
                .putBoolean("dispositivo_vinculado", false)
                .apply()

            startActivity(Intent(this, DevicesActivity::class.java))
            finish()
        }

//        btnIniciarSesion.setOnClickListener {
//            val correo = etUsuario.text.toString().trim()
//            val password = etPassword.text.toString().trim()
//
//            if (correo.isBlank() || password.isBlank()) {
//                Toast.makeText(this, "Ingresa correo y contraseña", Toast.LENGTH_SHORT).show()
//                return@setOnClickListener
//            }
//
//            btnIniciarSesion.isEnabled = true
//            btnIniciarSesion.text = "Iniciando..."
//
//            apiService.login(LoginRequest(correo, password)).enqueue(object : Callback<LoginResponse> {
//                override fun onResponse(call: Call<LoginResponse>, response: Response<LoginResponse>) {
//                    btnIniciarSesion.isEnabled = true
//                    btnIniciarSesion.text = "Iniciar Sesión"
//
//                    if (response.isSuccessful && response.body() != null) {
//                        val login = response.body()!!
//                        guardarSesion(login)
//                        cargarDispositivos(login.organizacionId)
//                    } else {
//                        Toast.makeText(this@MainActivity, "Credenciales inválidas", Toast.LENGTH_LONG).show()
//                    }
//                }
//
//                override fun onFailure(call: Call<LoginResponse>, t: Throwable) {
//                    btnIniciarSesion.isEnabled = true
//                    btnIniciarSesion.text = "Iniciar Sesión"
//                    Toast.makeText(this@MainActivity, "No se pudo contactar al servidor", Toast.LENGTH_LONG).show()
//                }
//            })
//        }
    }

    private fun guardarSesion(login: LoginResponse) {
        sharedPreferences.edit()
            .putInt("usuario_id", login.id)
            .putString("usuario_nombre", login.nombre)
            .putString("usuario_correo", login.correo)
            .putString("usuario_rol", login.rol)
            .putInt("organizacion_id", login.organizacionId)
            .apply()
    }

    private fun cargarDispositivos(organizacionId: Int) {
        apiService.obtenerDispositivos(organizacionId).enqueue(object : Callback<List<DispositivoResponse>> {
            override fun onResponse(call: Call<List<DispositivoResponse>>, response: Response<List<DispositivoResponse>>) {
                val dispositivos = response.body().orEmpty()
                val dispositivoActivo = dispositivos.firstOrNull { it.estado.equals("Activo", ignoreCase = true) }

                if (dispositivoActivo != null) {
                    sharedPreferences.edit()
                        .putString("dispositivo_mac", dispositivoActivo.macAddress)
                        .putBoolean("dispositivo_vinculado", true)
                        .apply()
                }

                val intent = Intent(this@MainActivity, DevicesActivity::class.java)
                startActivity(intent)
                finish()
            }

            override fun onFailure(call: Call<List<DispositivoResponse>>, t: Throwable) {
                val intent = Intent(this@MainActivity, DevicesActivity::class.java)
                startActivity(intent)
                finish()
            }
        })
    }
}