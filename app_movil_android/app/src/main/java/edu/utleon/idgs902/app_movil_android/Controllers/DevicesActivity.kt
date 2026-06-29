package edu.utleon.idgs902.app_movil_android.Controllers

import android.content.Intent
import android.os.Bundle
import android.widget.Button
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import edu.utleon.idgs902.app_movil_android.R

class DevicesActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_devices)

        val btnVincular = findViewById<Button>(R.id.btnVincular)

        // 2. Programamos la navegación al hacer clic en el botón
        btnVincular.setOnClickListener {
            // Creamos el puente (Intent) hacia la pantalla de Verificación
            val intent = Intent(this, VerificationActivity::class.java)
            startActivity(intent)
        }


        setupListInteractions()
    }


    private fun setupListInteractions() {
        //back
    }
}