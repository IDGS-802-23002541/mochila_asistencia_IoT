package edu.utleon.idgs902.app_movil_android.Utils

import android.annotation.SuppressLint
import android.bluetooth.*
import android.bluetooth.le.ScanCallback
import android.bluetooth.le.ScanFilter
import android.bluetooth.le.ScanResult
import android.bluetooth.le.ScanSettings
import android.content.Context
import android.os.Handler
import android.os.Looper
import android.util.Log
import java.util.*

/**
 * =============================================================================
 * PROYECTO   : Vision Guard — Mochila de Navegación Aumentada
 * ARCHIVO    : VisionGuardBleManager.kt
 * DESCRIPCIÓN: Controlador Android para escanear, conectar y enviar
 * comandos seriales UART (START / STOP) por BLE al ESP32.
 * =============================================================================
 */
@SuppressLint("MissingPermission")
class VisionGuardBleManager(private val context: Context, private val listener: BleStateListener) {

    private val bluetoothAdapter: BluetoothAdapter? by lazy {
        val bluetoothManager = context.getSystemService(Context.BLUETOOTH_SERVICE) as BluetoothManager
        bluetoothManager.adapter
    }

    private var bluetoothGatt: BluetoothGatt? = null
    private var rxCharacteristic: BluetoothGattCharacteristic? = null
    private var isConnected = false

    companion object {
        private const val TAG = "VisionGuardBleManager"

        // UUIDs estándar del servicio UART de perfil nórdico (Soportados por la ESP32)
        private val SERVICE_UUID = UUID.fromString("6E400001-B5A3-F393-E0A9-E50E24DCCA9E")
        private val RX_CHAR_UUID = UUID.fromString("6E400002-B5A3-F393-E0A9-E50E24DCCA9E") // Escritura (RX de la ESP32)
    }

    interface BleStateListener {
        fun onConectado()
        fun onDesconectado()
        fun onDispositivoEncontrado(nombre: String, mac: String)
        fun onError(mensaje: String)
        fun onAckRecibido(comando: String)
    }

    /**
     * Inicia el escaneo de dispositivos Bluetooth de bajo consumo de forma abierta.
     * Al omitir filtros lógicos del OS evitamos fallos internos de parsing en paquetes BLE.
     * ¡REQUERIMIENTO!: Exige tener habilitado el GPS y los permisos de Ubicación en el celular.
     */
    fun iniciarEscaneo() {
        val scanner = bluetoothAdapter?.bluetoothLeScanner
        if (scanner == null) {
            listener.onError("Bluetooth deshabilitado o no soportado en este teléfono móvil")
            return
        }

        val configuraciones = ScanSettings.Builder()
            .setScanMode(ScanSettings.SCAN_MODE_LOW_LATENCY)
            .build()

        Log.d(TAG, "Iniciando escaneo BLE abierto en busca de la mochila...")
        // Pasamos filtros en null para recibir todos los paquetes de publicidad del aire
        // y filtrarlos manualmente por código, resolviendo el problema de compatibilidad de marcas.
        scanner.startScan(null, configuraciones, scanCallback)
    }

    /**
     * Detiene el proceso de escaneo activo
     */
    fun detenerEscaneo() {
        try {
            bluetoothAdapter?.bluetoothLeScanner?.stopScan(scanCallback)
            Log.d(TAG, "Búsqueda Bluetooth detenida.")
        } catch (e: Exception) {
            Log.e(TAG, "Error al detener el escaneo: ${e.message}")
        }
    }

    private val scanCallback = object : ScanCallback() {
        override fun onScanResult(callbackType: Int, result: ScanResult) {
            val device = result.device
            val nombreDispositivo = result.scanRecord?.deviceName ?: device.name

            // Imprime en Logcat absolutamente todo lo que escuche tu antena para diagnóstico en vivo
            Log.d(TAG, "Dispositivo detectado -> Nombre: ${nombreDispositivo ?: "Anónimo/Oculto"} | MAC: [${device.address}]")

            // Filtrado manual altamente tolerante (Busca coincidencias parciales sin distinguir mayúsculas)
            if (nombreDispositivo != null) {
                val nombreUpper = nombreDispositivo.uppercase()
                if (nombreUpper.contains("VISIONGUARD") || nombreUpper.contains("SAFEPATH")) {
                    Log.d(TAG, "¡MOCHILA LOCALIZADA CON ÉXITO!: $nombreDispositivo [${device.address}]")
                    listener.onDispositivoEncontrado(nombreDispositivo, device.address)
                    detenerEscaneo()
                }
            }
        }

        override fun onScanFailed(errorCode: Int) {
            super.onScanFailed(errorCode)
            Log.e(TAG, "Fallo de escaneo BLE de Android. Código de error: $errorCode")
            listener.onError("Error de escaneo Bluetooth del sistema: $errorCode")
        }
    }

    /**
     * Conecta al servidor GATT del ESP32 utilizando su dirección física
     */
    fun conectar(direccionMac: String) {
        if (bluetoothGatt != null) {
            Log.w(TAG, "[Bluetooth] Cerrando instancia previa de GATT antes de reconectar...")
            bluetoothGatt?.disconnect()
            bluetoothGatt?.close()
            bluetoothGatt = null
        }

        val dispositivo = bluetoothAdapter?.getRemoteDevice(direccionMac) ?: return
        Log.d(TAG, "Conectando con la mochila por GATT a la MAC: $direccionMac...")

        // 2. Usar la bandera de autoConnect en false para ejecución inmediata
        bluetoothGatt = dispositivo.connectGatt(context, false, gattCallback)
//        val device = bluetoothAdapter?.getRemoteDevice(direccionMac)
//        if (device == null) {
//            listener.onError("Dirección MAC del dispositivo no válida")
//            return
//        }
//        Log.d(TAG, "Conectando con la mochila por GATT a la MAC: $direccionMac...")
//        bluetoothGatt = device.connectGatt(context, false, gattCallback)
    }

    /**
     * Cierra de forma segura el enlace activo con el hardware
     */
    fun desconectar() {
        limpiarConexion()
    }

    private val gattCallback = object : BluetoothGattCallback() {
        override fun onConnectionStateChange(gatt: BluetoothGatt, status: Int, newState: Int) {
            if (status == BluetoothGatt.GATT_SUCCESS) {
                if (newState == BluetoothProfile.STATE_CONNECTED) {
                    Log.i(TAG, "Conexión física establecida. Buscando canales de servicio...")
                    isConnected = true
                    Handler(Looper.getMainLooper()).post { listener.onConectado() }
                    gatt.discoverServices()
                } else if (newState == BluetoothProfile.STATE_DISCONNECTED) {
                    Log.i(TAG, "Mochila desconectada.")
                    limpiarConexion()
                }
            } else {
                Log.e(TAG, "Error en el canal GATT de enlace: $status")
                limpiarConexion()
                Handler(Looper.getMainLooper()).post { listener.onError("Fallo de enlace Bluetooth: $status") }
            }
        }

        override fun onServicesDiscovered(gatt: BluetoothGatt, status: Int) {
            if (status == BluetoothGatt.GATT_SUCCESS) {
                val service = gatt.getService(SERVICE_UUID)
                if (service != null) {
                    rxCharacteristic = service.getCharacteristic(RX_CHAR_UUID)
                    Log.i(TAG, "Canal de escritura serial UART BLE listo para enviar comandos.")
                } else {
                    Log.e(TAG, "El servicio UART de perfil nórdico no está disponible en este dispositivo.")
                }
            }
        }

        override fun onCharacteristicChanged(gatt: BluetoothGatt, characteristic: BluetoothGattCharacteristic) {
            super.onCharacteristicChanged(gatt, characteristic)

            // 1. Extraer los bytes crudos enviados por la mochila
            val data = characteristic.value ?: return
            val mensajeRecibido = String(data, Charsets.UTF_8).trim()

            Log.d(TAG, "[Bluetooth] Mensaje recibido del ESP32: '$mensajeRecibido'")

            // 2. Despachar el mensaje al hilo principal usando el Listener delegado
            if (mensajeRecibido == "ACK_START:OK" || mensajeRecibido == "ACK_STOP:OK") {
                Handler(Looper.getMainLooper()).post {
                    listener.onAckRecibido(mensajeRecibido)
                }
            }
        }

    }

    /**
     * Envía comando de Inicio ("START:recorridoId") al ESP32
     */
    fun enviarInicioRecorrido(recorridoId: Int) {
        val comando = "START:$recorridoId"
        enviarMensajeRaw(comando)
        Log.d(TAG, "Comando serial enviado: $comando")
    }

    /**
     * Envía comando de Parada ("STOP") al ESP32
     */
    fun enviarDetenerRecorrido() {
        val comando = "STOP"
        enviarMensajeRaw(comando)
        Log.d(TAG, "Comando serial enviado: STOP")
    }

    /**
     * Escribe bytes de datos UTF-8 directamente sobre la característica del ESP32
     */
    private fun enviarMensajeRaw(mensaje: String) {
        val characteristic = rxCharacteristic
        val gatt = bluetoothGatt
        if (characteristic == null || gatt == null || !isConnected) {
            listener.onError("El dispositivo móvil no está conectado a la mochila por Bluetooth")
            return
        }

        val bytes = mensaje.toByteArray(Charsets.UTF_8)
        characteristic.value = bytes
        characteristic.writeType = BluetoothGattCharacteristic.WRITE_TYPE_DEFAULT
        gatt.writeCharacteristic(characteristic)
    }

    /**
     * Libera los recursos de hardware utilizados por el adaptador GATT
     */
    private fun limpiarConexion() {
        isConnected = false
        rxCharacteristic = null
        try {
            bluetoothGatt?.close()
        } catch (e: Exception) {
            // Se ignoran fallos menores al liberar sockets cerrados
        }
        bluetoothGatt = null
        Handler(Looper.getMainLooper()).post { listener.onDesconectado() }
    }
}