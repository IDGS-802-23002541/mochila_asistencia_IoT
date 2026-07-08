package edu.utleon.idgs902.app_movil_android

import android.content.Intent
import android.os.Bundle
import android.widget.Button
import android.widget.EditText
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import edu.utleon.idgs902.app_movil_android.Controllers.DevicesActivity
import edu.utleon.idgs902.app_movil_android.Controllers.LoginActivity

class MainActivity : AppCompatActivity() {

    private val loginActivity = LoginActivity()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        val etUsuario = findViewById<EditText>(R.id.etUsuario)
        val etPassword = findViewById<EditText>(R.id.etPassword)
        val btnIniciarSesion = findViewById<Button>(R.id.btnIniciarSesion)

        btnIniciarSesion.setOnClickListener {
            val correo = etUsuario.text.toString().trim()
            val contrasena = etPassword.text.toString().trim()

            if (correo.isEmpty() || contrasena.isEmpty()) {
                Toast.makeText(this, "Completa correo y contraseña", Toast.LENGTH_SHORT).show()
                return@setOnClickListener
            }

            loginActivity.login(
                correo = correo,
                contrasena = contrasena,
                onSuccess = {
                    startActivity(Intent(this, DevicesActivity::class.java))
                    finish()
                },
                onError = { mensaje ->
                    Toast.makeText(this, mensaje, Toast.LENGTH_LONG).show()
                }
            )
        }
    }
}