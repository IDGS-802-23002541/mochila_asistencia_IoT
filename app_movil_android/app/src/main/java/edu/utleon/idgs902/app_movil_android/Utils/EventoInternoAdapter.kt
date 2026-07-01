package edu.utleon.idgs902.app_movil_android.Utils

import android.graphics.Color
import android.graphics.drawable.GradientDrawable
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.TextView
import androidx.recyclerview.widget.RecyclerView
import edu.utleon.idgs902.app_movil_android.R
import edu.utleon.idgs902.app_movil_android.Models.EventoRutaModels

class EventoInternoAdapter(private val listaEventos: List<EventoRutaModels>) :
    RecyclerView.Adapter<EventoInternoAdapter.EventoViewHolder>() {

    class EventoViewHolder(view: View) : RecyclerView.ViewHolder(view) {
        val indicadorColor: View = view.findViewById(R.id.viewIndicadorColor)
        val lblTexto: TextView = view.findViewById(R.id.lblTextoEvento)
        val lblHora: TextView = view.findViewById(R.id.lblHoraEvento)
    }

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): EventoViewHolder {
        val view = LayoutInflater.from(parent.context)
            .inflate(R.layout.item_evento_interno, parent, false)
        return EventoViewHolder(view)
    }

    override fun onBindViewHolder(holder: EventoViewHolder, position: Int) {
        val evento = listaEventos[position]
        holder.lblTexto.text = evento.tipo
        holder.lblHora.text = evento.hora

        // Cambiar el color del círculo en tiempo de ejecución
        val background = GradientDrawable().apply {
            shape = GradientDrawable.OVAL
            setColor(Color.parseColor(evento.colorHex))
        }
        holder.indicadorColor.background = background
    }

    override fun getItemCount(): Int = listaEventos.size
}