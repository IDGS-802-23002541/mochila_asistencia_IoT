package edu.utleon.idgs902.app_movil_android.Controllers

import android.content.Intent
import android.os.Bundle
import android.widget.Button
import android.widget.ImageView
import androidx.appcompat.app.AppCompatActivity
import edu.utleon.idgs902.app_movil_android.R

class VerificationActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_verification)

        val btnBack = findViewById<ImageView>(R.id.btnBack)
        val btnContinuar = findViewById<Button>(R.id.btnContinuar)

        // Acción para regresar a la pantalla anterior
        btnBack.setOnClickListener {
            finish()
        }

        // Acción para ir al Home / Monitoreo
        btnContinuar.setOnClickListener {
            val intent = Intent(this, HomeActivity::class.java)
            startActivity(intent)
        }
    }
}