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
import java.util.Date
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
                            adaptador.notifyDataSetChanged()
                        }
                        "Filtrar por fecha específica 📅" -> {
                            mostrarCalendarioFiltro()
                        }
                        "Rutas de esta semana 🗓️" -> {
                            filtrarRutasEstaSemana()
                            adaptador.notifyDataSetChanged()
                        }
                        "Con eventos registrados" -> {
                            val resultado = listaOriginal.filter { (it.eventos.toIntOrNull() ?: 0) > 0 }
                            listaFiltrada.clear()
                            listaFiltrada.addAll(resultado)
                            adaptador.notifyDataSetChanged()
                        }
                        "Sin eventos (Limpias)" -> {
                            val resultado = listaOriginal.filter { (it.eventos.toIntOrNull() ?: 0) == 0 }
                            listaFiltrada.clear()
                            listaFiltrada.addAll(resultado)
                            adaptador.notifyDataSetChanged()
                        }
                    }
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
        // TEMPORAL: hardcodeado para pruebas sin mochila física a la mano.
        // Revertir a esto cuando haya dispositivo real disponible:
        // val mac = sharedPreferences.getString("dispositivo_mac", null)

//        val mac = "94:B5:55:25:73:76"  // Dispositivo Id 10, mock v5

        // version chida
        val mac = sharedPreferences.getString("dispositivo_mac", null)

        if (mac.isNullOrBlank()) {
            Toast.makeText(this, "No hay dispositivo vinculado", Toast.LENGTH_SHORT).show()
            return
        }

        apiService.obtenerHistorialPorDispositivo(mac).enqueue(object : Callback<List<RecorridoHistorialResponse>> {
            override fun onResponse(
                call: Call<List<RecorridoHistorialResponse>>,
                response: Response<List<RecorridoHistorialResponse>>
            ) {
                if (response.isSuccessful && response.body() != null) {
                    val recorridosBackend = response.body()!!.map { item ->
                        RutaModels(
                            id = item.id.toString(),
                            fecha = formatearFecha(item.fechaInicio),
                            fechaRaw = parsearFechaISO(item.fechaInicio),
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

    // NUEVO: parseo de la fecha ISO cruda a Date real, para poder comparar rangos con precisión (año incluido)
    private fun parsearFechaISO(fechaIso: String): Date? {
        return try {
            val parser = SimpleDateFormat("yyyy-MM-dd'T'HH:mm:ss", Locale.US)
            parser.parse(fechaIso)
        } catch (_: Exception) {
            null
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

    // MODIFICADO: ahora pide fecha inicial y fecha final (rango), en vez de una sola fecha exacta.
    // Se mantiene el mismo punto de entrada del menú ("Filtrar por fecha específica").
    private fun mostrarCalendarioFiltro() {
        val calendario = Calendar.getInstance()

        // Paso 1: fecha de inicio del rango
        DatePickerDialog(this, { _, yearInicio, mesInicio, diaInicio ->
            val calInicio = Calendar.getInstance().apply {
                set(yearInicio, mesInicio, diaInicio, 0, 0, 0)
                set(Calendar.MILLISECOND, 0)
            }

            // Paso 2: fecha de fin del rango (se abre justo después de elegir la de inicio)
            DatePickerDialog(this, { _, yearFin, mesFin, diaFin ->
                val calFin = Calendar.getInstance().apply {
                    set(yearFin, mesFin, diaFin, 23, 59, 59)
                    set(Calendar.MILLISECOND, 999)
                }

                if (calFin.timeInMillis < calInicio.timeInMillis) {
                    Toast.makeText(this, "La fecha final no puede ser antes que la inicial", Toast.LENGTH_SHORT).show()
                    return@DatePickerDialog
                }

                val resultado = listaOriginal.filter { ruta ->
                    val f = ruta.fechaRaw ?: return@filter false
                    f.time in calInicio.timeInMillis..calFin.timeInMillis
                }

                listaFiltrada.clear()
                listaFiltrada.addAll(resultado)
                adaptador.notifyDataSetChanged()

            }, calendario.get(Calendar.YEAR), calendario.get(Calendar.MONTH), calendario.get(Calendar.DAY_OF_MONTH))
                .apply { setTitle("Selecciona fecha final") }
                .show()

        }, calendario.get(Calendar.YEAR), calendario.get(Calendar.MONTH), calendario.get(Calendar.DAY_OF_MONTH))
            .apply { setTitle("Selecciona fecha inicial") }
            .show()
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