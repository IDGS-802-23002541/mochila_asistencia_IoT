package edu.utleon.idgs902.app_movil_android.Controllers

import android.os.Bundle
import android.widget.Button
import androidx.appcompat.app.AppCompatActivity
import androidx.core.content.ContextCompat
import edu.utleon.idgs902.app_movil_android.R

class HomeActivity : AppCompatActivity() {

    private var isRunning = false

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_home)
        val bottomNavigation = findViewById<com.google.android.material.bottomnavigation.BottomNavigationView>(R.id.bottomNavigation)

        bottomNavigation.itemIconTintList = null
        bottomNavigation.selectedItemId = R.id.nav_home

        val btnAction = findViewById<Button>(R.id.btnIniciarRecorrido)

        btnAction.setOnClickListener {
            if (!isRunning) {
                // Cambiar a estado: Detener
                btnAction.text = "Detener"
                btnAction.background = ContextCompat.getDrawable(this, R.drawable.bg_button_outline_red)
                btnAction.setTextColor(ContextCompat.getColor(this, R.color.vg_red_error))
                isRunning = true
            } else {
                // Cambiar a estado: Iniciar
                btnAction.text = "Iniciar recorrido"
                btnAction.background = ContextCompat.getDrawable(this, R.drawable.bg_button_outline_blue)
                btnAction.setTextColor(ContextCompat.getColor(this, R.color.vg_dark_blue))
                isRunning = false
            }
        }
    }
}