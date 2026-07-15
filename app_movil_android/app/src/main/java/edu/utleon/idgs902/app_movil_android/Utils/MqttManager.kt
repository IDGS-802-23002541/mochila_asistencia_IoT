package edu.utleon.idgs902.app_movil_android.Utils

import android.content.Context
import android.util.Log
import info.mqtt.android.service.MqttAndroidClient
import org.eclipse.paho.client.mqttv3.*
import java.util.UUID

/**
 * =============================================================================
 * PROYECTO   : Vision Guard — Mochila de Navegación Aumentada
 * ARCHIVO    : MqttManager.kt
 * DESCRIPCIÓN: Controlador Android para conectarse, publicar y subscribirse al
 * broker de HiveMQ
 * VERSION: 1.0 Creación métodos comunicación MQTT
 * =============================================================================
 */

class MqttManager(private val context: Context, private val listener: MqttListener) {
    companion object {
        private const val TAG = "MqttManager"
    }
    private var conectado = false
    private val callbacks = mutableMapOf<String, (String) -> Unit>()
    private val clientId = MqttConfig.CLIENT_PREFIX + UUID.randomUUID()
    private val mqttClient = MqttAndroidClient(
        context,
        MqttConfig.SERVER_URI,
        clientId
    )
    interface MqttListener {
        fun onConectado()
        fun onDesconectado()
        fun onError(mensaje:String)
    }

    fun registrarCallback(topic:String, callback:(String)->Unit
    ){
        callbacks[topic]=callback
    }

    fun conectar(){
        Log.d(TAG,"Se solicitó conectar()")
        Log.d("MQTT", "Cliente = $mqttClient")
        Log.d("MQTT", "isConnected = ${mqttClient?.isConnected}")

        if (mqttClient.isConnected) {
            conectado = true
            return
        }
        val opciones = MqttConnectOptions().apply {
            userName = MqttConfig.USERNAME
            password = MqttConfig.PASSWORD.toCharArray()
            isAutomaticReconnect = true
            isCleanSession = true
            connectionTimeout = 10
            keepAliveInterval = 20
        }

        mqttClient.setCallback(object : MqttCallbackExtended{
            override fun connectComplete(reconnect:Boolean, serverURI:String?
            ){
                conectado=true
                listener.onConectado()
            }

            override fun connectionLost(cause:Throwable?){
                conectado=false
                listener.onDesconectado()
            }

            override fun messageArrived(topic:String?, message:MqttMessage?
            ){
                val payload = message?.toString() ?: ""
                Log.d(TAG, "Mensaje recibido [$topic] -> $payload")
                callbacks[topic]?.invoke(payload)
            }
            override fun deliveryComplete(token:IMqttDeliveryToken?){
            }
        })

        Log.d("MQTT", "Voy a ejecutar connect()")
        mqttClient.connect(opciones,null,object : IMqttActionListener{
                override fun onSuccess(asyncActionToken: IMqttToken?) {
                    Log.d("MQTT", "Conectado correctamente")
                    conectado = true
                    Log.d(TAG, "Conexión MQTT exitosa.")
                    listener.onConectado()
                }
                override fun onFailure(
                    asyncActionToken:IMqttToken?,
                    exception:Throwable?
                ){
                    conectado=false
                    listener.onError(
                        exception?.message
                            ?: "Error desconocido MQTT"
                    )
                }
            })
    }

    fun publicar(topic:String, mensaje:String): Boolean{
        if(!conectado){
            listener.onError(
                "No existe conexión MQTT."
            )
            return false
        }
        mqttClient.publish(topic, mensaje.toByteArray(), 1,false)
        return true
    }

    fun suscribirse(topic:String): Boolean{
        if(!conectado){
            return false
        }
        mqttClient.subscribe(topic,1)
        return true
    }

    fun cancelarSuscripcion(topic:String){
        mqttClient.unsubscribe(topic)
    }

    fun desconectar(){
        try{
            mqttClient.disconnect()
        }catch(_:Exception){}
        conectado=false
    }

    fun estaConectado():Boolean{
        return mqttClient.isConnected
    }
}