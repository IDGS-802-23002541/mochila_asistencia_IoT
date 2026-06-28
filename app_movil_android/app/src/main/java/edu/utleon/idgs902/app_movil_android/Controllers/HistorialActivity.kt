package edu.utleon.idgs902.app_movil_android.Controllers

import android.app.DatePickerDialog
import android.content.Intent
import android.os.Bundle
import android.widget.ArrayAdapter
import android.widget.TextView
import androidx.appcompat.app.AppCompatActivity
import androidx.appcompat.widget.ListPopupWindow
import androidx.core.content.ContextCompat
import androidx.recyclerview.widget.LinearLayoutManager
import androidx.recyclerview.widget.RecyclerView
import com.google.android.material.bottomnavigation.BottomNavigationView
import edu.utleon.idgs902.app_movil_android.R
import edu.utleon.idgs902.app_movil_android.Models.RutaModels
import edu.utleon.idgs902.app_movil_android.Utils.HistorialHelper
import edu.utleon.idgs902.app_movil_android.Utils.RutaAdapter
import java.text.SimpleDateFormat
import java.util.Calendar
import java.util.Locale

class HistorialActivity : AppCompatActivity() {

    private lateinit var listaOriginal: List<RutaModels>
    private var listaFiltrada: MutableList<RutaModels> = mutableListOf()

    private lateinit var adaptador: RutaAdapter
    private lateinit var rvHistorial: RecyclerView

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_historial)

        val bottomNavigation = findViewById<BottomNavigationView>(R.id.bottomNavigation)
        bottomNavigation.selectedItemId = R.id.nav_historial

        val btnFiltrar = findViewById<TextView>(R.id.btnFiltrar)
        val btnOrdenar = findViewById<TextView>(R.id.btnOrdenar)

        listaOriginal = HistorialHelper.obtenerRutas(this)
        listaFiltrada.addAll(listaOriginal)

        rvHistorial = findViewById(R.id.rvHistorial)
        rvHistorial.layoutManager = LinearLayoutManager(this)
        adaptador = RutaAdapter(listaFiltrada)
        rvHistorial.adapter = adaptador

        // 3. Configurar el nuevo menú del Botón FILTRAR
        btnFiltrar.setOnClickListener { vista ->
            val opciones = arrayOf(
                "Mostrar todos",
                "Filtrar por fecha específica 📅",
                "Rutas de esta semana 🗓️",
                "Con eventos registrados",
                "Sin eventos (Limpias)"
            )

            val listPopupWindow = ListPopupWindow(this).apply {
                anchorView = vista
                setAdapter(ArrayAdapter(this@HistorialActivity, R.layout.item_popup_personalizado, opciones))
                setBackgroundDrawable(ContextCompat.getDrawable(this@HistorialActivity, R.drawable.bg_popup_menu))
                width = 680
                verticalOffset = 10

                setOnItemClickListener { _, _, position, _ ->
                    when (opciones[position]) {
                        "Mostrar todos" -> {
                            listaFiltrada.clear()
                            listaFiltrada.addAll(listaOriginal)
                        }
                        "Filtrar por fecha específica 📅" -> {
                            mostrarCalendarioFiltro()
                        }
                        "Rutas de esta semana 🗓️" -> {
                            filtrarRutasEstaSemana()
                        }
                        "Con eventos registrados" -> {
                            val resultado = listaOriginal.filter { (it.eventos.toIntOrNull() ?: 0) > 0 }
                            listaFiltrada.clear()
                            listaFiltrada.addAll(resultado)
                        }
                        "Sin eventos (Limpias)" -> {
                            val resultado = listaOriginal.filter { (it.eventos.toIntOrNull() ?: 0) == 0 }
                            listaFiltrada.clear()
                            listaFiltrada.addAll(resultado)
                        }
                    }
                    adaptador.notifyDataSetChanged()
                    dismiss()
                }
            }
            listPopupWindow.show()
        }

        // 4. Configurar el nuevo menú del Botón ORDENAR (Incluye Orden Original)
        btnOrdenar.setOnClickListener { vista ->
            val opciones = arrayOf(
                "Más recientes primero ⏳",
                "Más antiguos primero",
                "Mayor cantidad de eventos 🚨",
                "Menor cantidad de eventos",
                "Mayor duración ⏱️",
                "Orden original"
            )

            val listPopupWindow = ListPopupWindow(this).apply {
                anchorView = vista
                setAdapter(ArrayAdapter(this@HistorialActivity, R.layout.item_popup_personalizado, opciones))
                setBackgroundDrawable(ContextCompat.getDrawable(this@HistorialActivity, R.drawable.bg_popup_menu))
                width = 750
                verticalOffset = 10

                setOnItemClickListener { _, _, position, _ ->
                    when (opciones[position]) {
                        "Más recientes primero ⏳" -> {
                            listaFiltrada.sortByDescending { it.id.toLongOrNull() ?: 0L }
                        }
                        "Más antiguos primero" -> {
                            listaFiltrada.sortBy { it.id.toLongOrNull() ?: 0L }
                        }
                        "Mayor cantidad de eventos 🚨" -> {
                            listaFiltrada.sortByDescending { it.eventos.toIntOrNull() ?: 0 }
                        }
                        "Menor cantidad de eventos" -> {
                            listaFiltrada.sortBy { it.eventos.toIntOrNull() ?: 0 }
                        }
                        "Mayor duración ⏱️" -> {
                            // Convierte los minutos a enteros para ordenar correctamente (ej: "32 min" -> 32)
                            listaFiltrada.sortByDescending { obtenerMinutosEnteros(it.duracion) }
                        }
                        "Orden original" -> {
                            // Al ordenarlo por ID de menor a mayor regresa a cómo se insertó originalmente
                            listaFiltrada.sortBy { it.id.toLongOrNull() ?: 0L }
                        }
                    }
                    adaptador.notifyDataSetChanged()
                    dismiss()
                }
            }
            listPopupWindow.show()
        }

        bottomNavigation.setOnItemSelectedListener { item ->
            when (item.itemId) {
                R.id.nav_home -> {
                    val intent = Intent(this, HomeActivity::class.java)
                    startActivity(intent)
                    overridePendingTransition(0, 0)
                    finish()
                    true
                }
                R.id.nav_historial -> true
                else -> false
            }
        }
    }

    private fun mostrarCalendarioFiltro() {
        val calendario = Calendar.getInstance()
        val año = calendario.get(Calendar.YEAR)
        val mes = calendario.get(Calendar.MONTH)
        val dia = calendario.get(Calendar.DAY_OF_MONTH)

        val datePickerDialog = DatePickerDialog(this, { _, year, month, dayOfMonth ->
            val calSeleccionado = Calendar.getInstance().apply {
                set(Calendar.YEAR, year)
                set(Calendar.MONTH, month)
                set(Calendar.DAY_OF_MONTH, dayOfMonth)
            }
            val sdf = SimpleDateFormat("dd 'de' MMMM", Locale("es", "MX"))
            val fechaSeleccionadaTexto = sdf.format(calSeleccionado.time)

            val resultado = listaOriginal.filter { ruta ->
                ruta.fecha.equals(fechaSeleccionadaTexto, ignoreCase = true)
            }

            listaFiltrada.clear()
            listaFiltrada.addAll(resultado)
            adaptador.notifyDataSetChanged()

        }, año, mes, dia)

        datePickerDialog.show()
    }

    // Filtra las rutas cuyo ID (Timestamp) pertenezca a los últimos 7 días
    private fun filtrarRutasEstaSemana() {
        val haceUnaSemana = System.currentTimeMillis() - (7 * 24 * 60 * 60 * 1000L)
        val resultado = listaOriginal.filter { ruta ->
            val timestampRuta = ruta.id.toLongOrNull() ?: 0L
            timestampRuta >= haceUnaSemana
        }
        listaFiltrada.clear()
        listaFiltrada.addAll(resultado)
    }

    // Helper para limpiar el texto "32 min" y dejar sólo el número 32 para poder ordenar numéricamente
    private fun obtenerMinutosEnteros(duracionTexto: String): Int {
        return duracionTexto.replace("[^0-9]".toRegex(), "").toIntOrNull() ?: 0
    }
}