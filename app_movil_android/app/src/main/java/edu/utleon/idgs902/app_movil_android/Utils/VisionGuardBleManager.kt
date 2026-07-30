package edu.utleon.idgs902.app_movil_android.Utils

import android.annotation.SuppressLint
import android.bluetooth.*
import android.bluetooth.le.ScanCallback
import android.bluetooth.le.ScanResult
import android.bluetooth.le.ScanSettings
import android.content.Context
import android.os.Handler
import android.os.Looper
import android.util.Log
import java.util.UUID

/**
 * =============================================================================
 * PROYECTO   : Vision Guard — Mochila de Navegación Aumentada
 * ARCHIVO    : VisionGuardBleManager.kt
 * DESCRIPCIÓN: Controlador Android para escanear y conectar al esp32
 * VERSION: 2.0 Se dejan los métodos unicos para la conexión BLE con el esp32 únicamente sin UART
 * =============================================================================
 */
@SuppressLint("MissingPermission")
class VisionGuardBleManager(private val context: Context, private val listener: BleStateListener) {

    private val bluetoothAdapter: BluetoothAdapter? by lazy {
        val bluetoothManager = context.getSystemService(Context.BLUETOOTH_SERVICE) as BluetoothManager
        bluetoothManager.adapter
    }

    private var bluetoothGatt: BluetoothGatt? = null
    private var isConnected = false

    companion object {
        private const val TAG = "VisionGuardBleManager"

    }

    interface BleStateListener {
        fun onConectado()
        fun onDesconectado()
        fun onDispositivoEncontrado(nombre: String, mac: String)
        fun onError(mensaje: String)
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
        // Busca por 10 segundos
        Handler(Looper.getMainLooper()).postDelayed({
            detenerEscaneo()
            if (!isConnected) {
                listener.onError("No se encontró ninguna mochila Vision Guard.")
            }
        }, 10000) // 10 segundos
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
                // Filtro nombre esp32
                if (nombreDispositivo?.equals("vision_guard_esp32", true) == true) {
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

        val dispositivo = bluetoothAdapter?.getRemoteDevice(direccionMac)
        if (dispositivo == null) {
            listener.onError("Dirección MAC inválida.")
            return
        }
        Log.d(TAG, "Conectando con la mochila por GATT a la MAC: $direccionMac...")

        // 2. Usar la bandera de autoConnect en false para ejecución inmediata
        bluetoothGatt = dispositivo.connectGatt(context, false, gattCallback)
    }

    /**
     * Cierra de forma segura el enlace activo con el hardware
     */
    fun desconectar() {
        bluetoothGatt?.disconnect()
    }

    private val gattCallback = object : BluetoothGattCallback() {
        override fun onConnectionStateChange(gatt: BluetoothGatt, status: Int, newState: Int) {
            if (status == BluetoothGatt.GATT_SUCCESS) {
                if (newState == BluetoothProfile.STATE_CONNECTED) {
                    Log.i(TAG, "Conexión física establecida. Buscando canales de servicio...")
                    isConnected = true
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
            if (status != BluetoothGatt.GATT_SUCCESS) {
                listener.onError("No fue posible descubrir los servicios BLE.")
                return
            }
            val servicio = gatt.getService(
                UUID.fromString("12345678-1234-5678-1234-56789abcdef0")
            )
            if (servicio != null) {
                Log.i(TAG, "Servicio Vision Guard encontrado.")
                Handler(Looper.getMainLooper()).post {
                    listener.onConectado()
                }
            } else {
                listener.onError("El dispositivo encontrado no es una mochila Vision Guard.")
                gatt.disconnect()
            }
        }
    }
    /**
     * Libera los recursos de hardware utilizados por el adaptador GATT
     */
    private fun limpiarConexion() {
        isConnected = false

        try {
            bluetoothGatt?.disconnect()
        } catch (_: Exception) {
        }
        try {
            bluetoothGatt?.close()
        } catch (_: Exception) {
        }

        bluetoothGatt = null

        Handler(Looper.getMainLooper()).post {
            listener.onDesconectado()
        }

        Log.d(TAG, "Conexión BLE liberada.")
    }
}

