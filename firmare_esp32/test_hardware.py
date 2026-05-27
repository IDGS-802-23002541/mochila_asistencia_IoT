# =============================================================================
# PROYECTO   : Safe-Path AI — Sistema de Navegación Aumentada
# ARCHIVO    : test_hardware.py
# DESCRIPCIÓN: Script de prueba unitaria para validar la biblioteca HAL
#              (dispositivos.py) antes de integrar con MQTT y Firebase.
#              Ejecutar directamente en la ESP32 / ESP32-CAM.
# INTEGRANTES: [Nombres del equipo Safe-Path AI]
# VERSIÓN    : 1.0
# =============================================================================
#
# INSTRUCCIONES DE USO:
#   1. Copiar a la ESP32:  dispositivos.py, hcsr04.py, imu.py, vector3d.py
#   2. Copiar este archivo como main.py (o ejecutar desde Thonny).
#   3. Abrir el monitor serie y observar los resultados de cada prueba.
#   4. Cada prueba imprime [OK] o [FALLO] con descripción del error.
#
# CRITERIO DE APROBACIÓN (rúbrica E1):
#   - Todas las pruebas imprimen [OK]
#   - Ningún machine.Pin aparece en este archivo
#   - El resumen global tiene las 4 claves esperadas
# =============================================================================

import time
from dispositivos import SensorBox, ActuatorBox

# ─────────────────────────────────────────────────────────────────────────────
# Utilidad: imprimir resultado de prueba
# ─────────────────────────────────────────────────────────────────────────────
def resultado(nombre_prueba, condicion, detalle=""):
    etiqueta = "[OK]   " if condicion else "[FALLO]"
    print(f"  {etiqueta} {nombre_prueba}", end="")
    if detalle:
        print(f" — {detalle}", end="")
    print()
    return condicion


# ─────────────────────────────────────────────────────────────────────────────
# PRUEBA 1: Instanciación de SensorBox
# ─────────────────────────────────────────────────────────────────────────────
def prueba_instanciacion_sensor():
    print("\n[TEST 1] Instanciación SensorBox")
    try:
        caja = SensorBox()
        resultado("SensorBox() sin excepciones", True)
        return caja
    except Exception as e:
        resultado("SensorBox() sin excepciones", False, str(e))
        return None


# ─────────────────────────────────────────────────────────────────────────────
# PRUEBA 2: leer_distancia_cm — tipo y rango
# ─────────────────────────────────────────────────────────────────────────────
def prueba_distancia(caja):
    print("\n[TEST 2] leer_distancia_cm()")
    dist = caja.leer_distancia_cm()

    # Acepta None (fuera de rango) o un float válido
    tipo_valido = dist is None or isinstance(dist, float)
    resultado("Devuelve float o None", tipo_valido, f"valor={dist}")

    if dist is not None:
        rango_valido = 2.0 <= dist <= 400.0
        resultado("Valor dentro de rango físico (2-400 cm)", rango_valido, f"{dist:.1f} cm")


# ─────────────────────────────────────────────────────────────────────────────
# PRUEBA 3: esta_oscuro — tipo de retorno
# ─────────────────────────────────────────────────────────────────────────────
def prueba_ldr(caja):
    print("\n[TEST 3] esta_oscuro()")
    val = caja.esta_oscuro()
    resultado("Devuelve bool", isinstance(val, bool), f"valor={val}")

    # Prueba con umbral explícito
    val_alto  = caja.esta_oscuro(umbral=4095)  # siempre oscuro
    val_bajo  = caja.esta_oscuro(umbral=0)     # nunca oscuro
    resultado("umbral=4095 → siempre True",  val_alto is True,  f"retornó {val_alto}")
    resultado("umbral=0    → siempre False", val_bajo is False, f"retornó {val_bajo}")


# ─────────────────────────────────────────────────────────────────────────────
# PRUEBA 4: detectar_caida — tipo de retorno
# ─────────────────────────────────────────────────────────────────────────────
def prueba_caida(caja):
    print("\n[TEST 4] detectar_caida()")
    val = caja.detectar_caida()
    resultado("Devuelve bool", isinstance(val, bool), f"valor={val}")

    # En reposo no debería disparar la alarma de caída
    resultado("En reposo → False (umbral 2g)", val is False,
              "Si es True, verificar que el dispositivo esté en reposo")


# ─────────────────────────────────────────────────────────────────────────────
# PRUEBA 5: obtener_resumen_global — estructura del diccionario
# ─────────────────────────────────────────────────────────────────────────────
def prueba_resumen_global(caja):
    print("\n[TEST 5] obtener_resumen_global()")
    resumen = caja.obtener_resumen_global()

    resultado("Devuelve dict", isinstance(resumen, dict), f"tipo={type(resumen)}")

    claves_esperadas = ["distancia_cm", "oscuro", "caida", "temperatura"]
    for clave in claves_esperadas:
        resultado(f"Clave '{clave}' presente", clave in resumen,
                  f"valor={resumen.get(clave)}")

    # Tipos de cada campo
    if "oscuro" in resumen:
        resultado("'oscuro' es bool", isinstance(resumen["oscuro"], bool))
    if "caida" in resumen:
        resultado("'caida' es bool", isinstance(resumen["caida"], bool))
    if "temperatura" in resumen:
        resultado("'temperatura' es numérico",
                  isinstance(resumen["temperatura"], (int, float)),
                  f"{resumen.get('temperatura', '?'):.1f} °C")

    return resumen


# ─────────────────────────────────────────────────────────────────────────────
# PRUEBA 6: ActuatorBox — instanciación sin error
# ─────────────────────────────────────────────────────────────────────────────
def prueba_instanciacion_actuador():
    print("\n[TEST 6] Instanciación ActuatorBox")
    try:
        actuadores = ActuatorBox()
        resultado("ActuatorBox() sin excepciones", True)
        return actuadores
    except Exception as e:
        resultado("ActuatorBox() sin excepciones", False, str(e))
        return None


# ─────────────────────────────────────────────────────────────────────────────
# PRUEBA 7: Motor vibrador — pulso corto
# ─────────────────────────────────────────────────────────────────────────────
def prueba_motor(actuadores):
    print("\n[TEST 7] activar_vibracion(duracion_ms=200)")
    try:
        actuadores.activar_vibracion(duracion_ms=200)
        resultado("Motor vibrador activado sin excepción", True,
                  "Debes sentir un pulso de ~200ms")
    except Exception as e:
        resultado("Motor vibrador activado sin excepción", False, str(e))


# ─────────────────────────────────────────────────────────────────────────────
# PRUEBA 8: Buzzer — alerta crítica 2 pulsos
# ─────────────────────────────────────────────────────────────────────────────
def prueba_buzzer(actuadores):
    print("\n[TEST 8] alerta_critica(pulsos=2)")
    try:
        actuadores.alerta_critica(pulsos=2, duracion_ms=150, cooldown_ms=0)
        resultado("Buzzer activado sin excepción", True,
                  "Debes escuchar 2 pitidos cortos")
    except Exception as e:
        resultado("Buzzer activado sin excepción", False, str(e))


# ─────────────────────────────────────────────────────────────────────────────
# PRUEBA 9: silenciar_todo — apaga todos los actuadores
# ─────────────────────────────────────────────────────────────────────────────
def prueba_silencio(actuadores):
    print("\n[TEST 9] silenciar_todo()")
    try:
        actuadores.silenciar_todo()
        resultado("silenciar_todo() sin excepción", True)
    except Exception as e:
        resultado("silenciar_todo() sin excepción", False, str(e))


# ─────────────────────────────────────────────────────────────────────────────
# PRUEBA 10: Lectura continua durante 5 iteraciones (integración básica)
# ─────────────────────────────────────────────────────────────────────────────
def prueba_lectura_continua(caja, iteraciones=5):
    print(f"\n[TEST 10] Lectura continua — {iteraciones} iteraciones")
    exitos = 0
    for i in range(iteraciones):
        try:
            r = caja.obtener_resumen_global()
            print(f"    iter {i+1}: dist={r['distancia_cm']} | oscuro={r['oscuro']} "
                  f"| caida={r['caida']} | temp={r['temperatura']:.1f}°C")
            exitos += 1
        except Exception as e:
            print(f"    iter {i+1}: ERROR — {e}")
        time.sleep(0.5)

    resultado(f"{iteraciones}/{iteraciones} lecturas exitosas",
              exitos == iteraciones,
              f"{exitos} exitosas de {iteraciones}")


# ─────────────────────────────────────────────────────────────────────────────
# MAIN: ejecutar todas las pruebas en secuencia
# ─────────────────────────────────────────────────────────────────────────────
def main():
    print("=" * 55)
    print("  Safe-Path AI — TEST SUITE E1: Biblioteca HAL")
    print("=" * 55)

    # ── Sensores ──────────────────────────────────────────────────────────────
    caja = prueba_instanciacion_sensor()
    if caja is None:
        print("\n[FATAL] No se pudo crear SensorBox. Revisa el cableado I2C y pines.")
        return

    prueba_distancia(caja)
    prueba_ldr(caja)
    prueba_caida(caja)
    resumen = prueba_resumen_global(caja)

    # ── Actuadores ────────────────────────────────────────────────────────────
    actuadores = prueba_instanciacion_actuador()
    if actuadores is not None:
        prueba_motor(actuadores)
        time.sleep(1)
        prueba_buzzer(actuadores)
        prueba_silencio(actuadores)

    # ── Integración básica ────────────────────────────────────────────────────
    prueba_lectura_continua(caja)

    print("\n" + "=" * 55)
    print("  FIN DEL TEST SUITE")
    print("  Revisa los [FALLO] y corrígelos antes de continuar con E2.")
    print("=" * 55)


# Punto de entrada — también funciona si se copia como main.py en la ESP32
main()
