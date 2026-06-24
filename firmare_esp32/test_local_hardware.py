# =============================================================================
# PROYECTO   : Vision Guard
# ARCHIVO    : test_local_hardware.py
# DESCRIPCIÓN: Script de prueba unitaria local (Offline) para validar las
#              conexiones de los sensores, motor vibrador, buzzer y DFPlayer
#              usando la biblioteca HAL (dispositivos.py).
#              No requiere conexión a WiFi ni configuración de MQTT.
# INSTRUCCIONES:
#   1. Sube a la ESP32 los archivos: hcsr04.py, imu.py, vector3d.py
#   2. Sube a la ESP32 el archivo de la HAL: dispositivos.py (v2.2)
#   3. Ejecuta este script desde Thonny (F5) y abre el monitor serial.
# =============================================================================

from dispositivos import SensorBox, ActuatorBoxs
import time

def ejecutar_pruebas():
    print("=" * 60)
    print("    VISION GUARD — TEST DE DIAGNÓSTICO DE HARDWARE LOCAL")
    print("=" * 60)
    
    # ─────────────────────────────────────────────────────────────────────────
    # PASO 1: INSTANCIACIÓN DE LA HAL
    # ─────────────────────────────────────────────────────────────────────────
    print("\n[1/4] Inicializando Capa de Abstracción de Hardware (HAL)...")
    try:
        # SensorBox utiliza: trig=12, echo=13, ir_izq=14, ir_der=27, scl=22, sda=21
        sensores = SensorBox()
        # ActuatorBox utiliza: tx_dfplayer=26, rx_dfplayer=25, pin_motor=33, pin_buzzer=2
        actuadores = ActuatorBox()
        print("-> [OK] HAL instanciada correctamente.")
    except Exception as e:
        print("-> [FALLO CRÍTICO] Error al instanciar la HAL:", e)
        print("   Verifica que 'dispositivos.py', 'hcsr04.py' e 'imu.py' estén en el ESP32.")
        return

    # ─────────────────────────────────────────────────────────────────────────
    # PASO 2: PRUEBA INDIVIDUAL DE ACTUADORES
    # ─────────────────────────────────────────────────────────────────────────
    print("\n[2/4] Iniciando ciclo de prueba de Actuadores...")
    
    # A. Prueba del Motor Vibrador Háptico (GPIO 33)
    print("   -> Activando Motor Vibrador Háptico (FS100A/LED)...")
    actuadores.activar_alerta_haptica()
    time.sleep(1.5)
    actuadores.desactivar_alerta_haptica()
    print("   -> Motor apagado.")
    time.sleep(0.5)

    # B. Prueba del Buzzer de Proximidad (GPIO 2)
    print("   -> Encendiendo Buzzer Activo...")
    actuadores.encender_buzzer()
    time.sleep(0.5)
    actuadores.apagar_buzzer()
    print("   -> Buzzer apagado.")
    time.sleep(0.5)

    # C. Prueba de comandos seriales al DFPlayer Mini
    print("   -> Enviando comando de prueba al DFPlayer Mini...")
    # Intenta reproducir la pista #1 (Obstáculo frontal)
    actuadores.reproducir_audio(ActuatorBox.PISTA_OBSTACULO_FRONTAL)
    print("   -> Comando enviado (Pista #1). Verifica si se escucha la bocina.")
    time.sleep(4.0) # Tiempo para escuchar el audio completo
    
    actuadores.silenciar_todo()

    # ─────────────────────────────────────────────────────────────────────────
    # PASO 3: PRUEBA DE SENSORES EN TIEMPO REAL
    # ─────────────────────────────────────────────────────────────────────────
    print("\n[3/4] Iniciando lectura interactiva de Sensores (Duración: 15 seg)...")
    print("   Mueve el obstáculo frente al ultrasónico, togglea los switches IR")
    print("   y mueve el acelerómetro para probar la fuerza G.")
    print("-" * 60)
    
    inicio_test = time.time()
    while time.time() - inicio_test < 15:
        # Lectura de proximidad
        dist = sensores.leer_distancia_cm()
        
        # Lectura de interruptores (0 / True representa obstáculo en el sensor real)
        ir_izq = sensores.leer_ir_izquierdo()
        ir_der = sensores.leer_ir_derecho()
        
        # Lectura de caída (fuerza G > 2.5G)
        caida = sensores.detectar_caida()
        
        # Imprimir telemetría formateada
        print(f"Distancia: {dist:.1f} cm | IR Izq: {ir_izq} | IR Der: {ir_der} | Caída: {caida}")
        
        # Reacción háptica interactiva instantánea
        if dist <= 30.0 or ir_izq or ir_der or caida:
            actuadores.activar_alerta_haptica()
        else:
            actuadores.desactivar_alerta_haptica()
            
        # Reacción acústica interactiva del buzzer
        actuadores.actualizar_alerta_distancia(dist)
        
        time.sleep(0.3) # Muestreo rápido

    # ─────────────────────────────────────────────────────────────────────────
    # PASO 4: APAGADO SEGURO
    # ─────────────────────────────────────────────────────────────────────────
    print("-" * 60)
    print("[4/4] Limpiando estados físicos y activando Modo Seguro...")
    actuadores.silenciar_todo()
    print("\n=======================================================")
    print("      DIAGNÓSTICO FINALIZADO CON ÉXITO")
    print("=======================================================")

# Ejecución de la prueba
if __name__ == '__main__':
    ejecutar_pruebas()