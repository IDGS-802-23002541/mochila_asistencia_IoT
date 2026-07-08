package edu.utleon.idgs902.app_movil_android.Controllers

import android.app.DatePickerDialog
import android.content.Context
import android.content.Intent
import android.content.SharedPreferences
import android.os.Bundle
import android.widget.ArrayAdapter
import android.widget.TextView
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import androidx.appcompat.widget.ListPopupWindow
import androidx.core.content.ContextCompat
import androidx.recyclerview.widget.LinearLayoutManager
import androidx.recyclerview.widget.RecyclerView
import com.google.android.material.bottomnavigation.BottomNavigationView
import edu.utleon.idgs902.app_movil_android.R
import edu.utleon.idgs902.app_movil_android.Models.RutaModels
import edu.utleon.idgs902.app_movil_android.Utils.RutaAdapter
import edu.utleon.idgs902.app_movil_android.Utils.RecorridoHistorialResponse
import edu.utleon.idgs902.app_movil_android.Utils.VisionGuardApiService
import retrofit2.Call
import retrofit2.Callback
import retrofit2.Response
import java.text.SimpleDateFormat
import java.util.Calendar
import java.util.Locale

class HistorialActivity : AppCompatActivity() {

    private lateinit var listaOriginal: List<RutaModels>
    private var listaFiltrada: MutableList<RutaModels> = mutableListOf()

    private lateinit var adaptador: RutaAdapter
    private lateinit var rvHistorial: RecyclerView
    private lateinit var sharedPreferences: SharedPreferences
    private val apiService = VisionGuardApiService.create()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_historial)

        val bottomNavigation = findViewById<BottomNavigationView>(R.id.bottomNavigation)
        bottomNavigation.selectedItemId = R.id.nav_historial

        val btnFiltrar = findViewById<TextView>(R.id.btnFiltrar)
        val btnOrdenar = findViewById<TextView>(R.id.btnOrdenar)
        sharedPreferences = getSharedPreferences("VisionGuardPrefs", Context.MODE_PRIVATE)

        listaOriginal = emptyList()
        listaFiltrada.clear()

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

        cargarHistorialDesdeServidor()
    }

    private fun cargarHistorialDesdeServidor() {
        val organizacionId = sharedPreferences.getInt("organizacion_id", -1)
        if (organizacionId <= 0) {
            return
        }

        apiService.obtenerHistorialPorOrganizacion(organizacionId).enqueue(object : Callback<List<RecorridoHistorialResponse>> {
            override fun onResponse(
                call: Call<List<RecorridoHistorialResponse>>,
                response: Response<List<RecorridoHistorialResponse>>
            ) {
                if (response.isSuccessful && response.body() != null) {
                    val recorridosBackend = response.body()!!.map { item ->
                        RutaModels(
                            id = item.id.toString(),
                            fecha = formatearFecha(item.fechaInicio),
                            duracion = formatearDuracion(item.duracionSegundos),
                            obstaculos = "0",
                            caidas = "0",
                            eventos = item.totalEventos.toString(),
                            distancia = formatearDistancia(item.distanciaTotalMetros)
                        )
                    }

                    listaOriginal = recorridosBackend
                    listaFiltrada.clear()
                    listaFiltrada.addAll(listaOriginal)
                    adaptador = RutaAdapter(listaFiltrada)
                    rvHistorial.adapter = adaptador
                    adaptador.notifyDataSetChanged()
                } else {
                    Toast.makeText(this@HistorialActivity, "No se pudo cargar el historial del servidor", Toast.LENGTH_SHORT).show()
                }
            }

            override fun onFailure(call: Call<List<RecorridoHistorialResponse>>, t: Throwable) {
                Toast.makeText(this@HistorialActivity, "Error al consultar el historial", Toast.LENGTH_SHORT).show()
            }
        })
    }

    private fun formatearFecha(fechaIso: String): String {
        return try {
            val parser = SimpleDateFormat("yyyy-MM-dd'T'HH:mm:ss", Locale.US)
            val date = parser.parse(fechaIso)
            val sdf = SimpleDateFormat("dd 'de' MMMM", Locale("es", "MX"))
            sdf.format(date)
        } catch (_: Exception) {
            fechaIso
        }
    }

    private fun formatearDuracion(segundos: Double): String {
        val minutos = (segundos / 60).toInt()
        return if (minutos > 0) "$minutos min" else "0 min"
    }

    private fun formatearDistancia(metros: Double): String {
        return if (metros >= 1000) {
            String.format(Locale.US, "%.2f km", metros / 1000.0)
        } else {
            String.format(Locale.US, "%.0f m", metros)
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