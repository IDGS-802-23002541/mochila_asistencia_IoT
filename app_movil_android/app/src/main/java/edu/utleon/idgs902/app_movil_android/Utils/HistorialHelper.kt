package edu.utleon.idgs902.app_movil_android.Utils

import android.content.Context
import com.google.gson.Gson
import com.google.gson.reflect.TypeToken
import edu.utleon.idgs902.app_movil_android.Models.RutaModels

object HistorialHelper {
    private const val PREFS_NAME = "HistorialPrefs"
    private const val KEY_ROUTES = "lista_rutas"

    // Guardar una nueva ruta al principio de la lista
    fun guardarRuta(context: Context, nuevaRuta: RutaModels) {
        val prefs = context.getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE)
        val rutasActuales = obtenerRutas(context).toMutableList()
        rutasActuales.add(0, nuevaRuta) // La más reciente va primero

        val json = Gson().toJson(rutasActuales)
        prefs.edit().putString(KEY_ROUTES, json).apply()
    }

    // Obtener todas las rutas guardadas
    fun obtenerRutas(context: Context): List<RutaModels> {
        val prefs = context.getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE)
        val json = prefs.getString(KEY_ROUTES, null) ?: return emptyList()
        val type = object : TypeToken<List<RutaModels>>() {}.type // Ahora sí funcionará perfecto
        return Gson().fromJson(json, type)
    }
}