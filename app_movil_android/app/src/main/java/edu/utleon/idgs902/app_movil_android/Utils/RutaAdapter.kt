package edu.utleon.idgs902.app_movil_android.Utils

import android.content.Intent
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.TextView
import androidx.recyclerview.widget.RecyclerView
import edu.utleon.idgs902.app_movil_android.R
import edu.utleon.idgs902.app_movil_android.Models.RutaModels
import edu.utleon.idgs902.app_movil_android.Controllers.DetallesRutaActivity

class RutaAdapter(private val listaRutas: List<RutaModels>) :
    RecyclerView.Adapter<RutaAdapter.RutaViewHolder>() {

    class RutaViewHolder(view: View) : RecyclerView.ViewHolder(view) {
        val lblNombre: TextView = view.findViewById(R.id.lblNombreRuta)
        val lblDetalles: TextView = view.findViewById(R.id.lblDetallesRuta)
    }

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): RutaViewHolder {
        val view = LayoutInflater.from(parent.context)
            .inflate(R.layout.item_ruta, parent, false)
        return RutaViewHolder(view)
    }

    override fun onBindViewHolder(holder: RutaViewHolder, position: Int) {
        val ruta = listaRutas[position]

        val numeroRealRuta = position + 1
        val nombreMostrar = "Ruta #$numeroRealRuta"

        holder.lblNombre.text = nombreMostrar
        holder.lblDetalles.text = "${ruta.fecha} · ${ruta.duracion} · ${ruta.eventos} eventos"

        holder.itemView.setOnClickListener {
            val intent = Intent(holder.itemView.context, DetallesRutaActivity::class.java).apply {
                // Pasamos el ID string para que DetallesRutaActivity lo reciba e invoque a Retrofit
                putExtra("RECORRIDO_ID", ruta.id)

                putExtra("NUMERO_RUTA", nombreMostrar)
                putExtra("FECHA", ruta.fecha)
                putExtra("DURACION", ruta.duracion)
                putExtra("CANTIDAD_EVENTOS", ruta.eventos)
                putExtra("DISTANCIA", ruta.distancia)
            }
            holder.itemView.context.startActivity(intent)
        }
    }

    override fun getItemCount(): Int = listaRutas.size
}