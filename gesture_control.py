"""
Sistema de control de iluminación basado en gestos de mano
Universidad Militar Nueva Granada - Ingeniería Mecatrónica

Usa MediaPipe Gesture Recognizer para detectar gestos con la cámara
y envía comandos por puerto Serial (USB) al ESP32 para controlar LEDs.

Gestos:
    Closed_Fist  -> Intensidad 30%
    Victory      -> Intensidad 70%
    Open_Palm    -> Intensidad 100%
    Thumb_Down   -> Interrupción 1 (Modo 1: secuencia de luces)
    Thumb_Up     -> Interrupción 2 (Modo 2: secuencia de luces)

Además: si pasan IDLE_TIMEOUT segundos sin detectar ningún gesto
válido, se envía automáticamente un comando de apagado (OFF_COMMAND).

FLUJO GENERAL DEL PROGRAMA (resumen):
    1. Se abre la cámara y se toma un frame (foto) muchas veces por segundo.
    2. Cada frame se le pasa al modelo de MediaPipe, que devuelve qué
       gesto detectó y con qué confianza (score de 0 a 1).
    3. Si el gesto detectado tiene un comando asociado, se envía ese
       comando como texto por el puerto Serial (el mismo cable USB
       que usas para programar el ESP32 sirve para esto).
    4. Si pasan varios segundos sin ningún gesto válido, se envía un
       comando de apagado automático.
    5. El ESP32, por su lado, está todo el tiempo "escuchando" ese
       puerto Serial y reacciona cuando le llega un comando (ver
       esp32_firmware.ino).
"""

import cv2
import mediapipe as mp
import serial
import serial.tools.list_ports
import time

from mediapipe.tasks import python
from mediapipe.tasks.python import vision

# ------------------- CONFIGURACIÓN -------------------
MODEL_PATH = "gesture_recognizer.task"   # Modelo pre-entrenado de MediaPipe (se descarga aparte, ver README)
SERIAL_PORT = "COM3"                     # Windows: COM3, COM4... | Linux/Mac: /dev/ttyUSB0, /dev/ttyACM0
BAUD_RATE = 115200                       # Debe ser IGUAL al valor puesto en Serial.begin() del firmware .ino
DEBOUNCE_SECONDS = 1.0                   # Tiempo mínimo (en segundos) entre envíos del mismo gesto

IDLE_TIMEOUT = 3.0                      # Segundos sin gestos válidos antes de apagar automáticamente
OFF_COMMAND = "I0\n"                     # Comando que le dice al ESP32 que apague la luz

# Mapeo gesto -> comando enviado al ESP32.
# Es un protocolo muy simple: solo texto plano terminado en "\n".
# El "\n" es importante porque en el ESP32 usamos
# Serial.readStringUntil('\n') para saber dónde termina cada comando.
GESTURE_COMMANDS = {
    "Closed_Fist": "I30\n",
    "Victory":     "I70\n",
    "Open_Palm":   "I100\n",
    "Thumb_Down":  "M1\n",
    "Thumb_Up":    "M2\n",
}

# Solo para mostrar texto más amigable en pantalla (no afecta la lógica)
GESTURE_LABELS_ES = {
    "Closed_Fist": "Puño cerrado (30%)",
    "Victory":     "Paz / Victoria (70%)",
    "Open_Palm":   "Mano abierta (100%)",
    "Thumb_Down":  "Pulgar abajo (Modo 1)",
    "Thumb_Up":    "Pulgar arriba (Modo 2)",
    "None":        "Sin gesto",
}


def listar_puertos_disponibles():
    """
    Muestra en consola los puertos seriales que la PC detecta conectados.
    Sirve para saber qué poner en SERIAL_PORT si no sabes cuál es
    (por ejemplo, si el ESP32 no aparece como COM3 sino como COM5).
    """
    puertos = serial.tools.list_ports.comports()
    print("Puertos seriales detectados:")
    for p in puertos:
        print(f"  - {p.device}: {p.description}")


def conectar_esp32(puerto, baud):
    """
    Intenta abrir la conexión Serial con el ESP32.
    Si falla (ej. el ESP32 no está conectado, o el puerto es
    incorrecto), el programa NO se detiene: sigue funcionando
    solo con la parte de visión, pero sin poder enviar comandos.
    Esto es útil mientras pruebas la detección de gestos sin
    tener el hardware conectado todavía.
    """
    try:
        ser = serial.Serial(puerto, baud, timeout=1)
        # El ESP32 se reinicia automáticamente cuando se abre el
        # puerto Serial desde la PC. Este delay le da tiempo a
        # terminar de arrancar antes de empezar a mandarle comandos.
        time.sleep(2)
        print(f"[OK] Conectado al ESP32 en {puerto}")
        return ser
    except Exception as e:
        print(f"[AVISO] No se pudo conectar al ESP32 ({e}). "
              f"El programa seguirá funcionando solo con visión, sin enviar comandos.")
        return None


def main():
    listar_puertos_disponibles()

    # ---------- 1) Inicializar el Gesture Recognizer de MediaPipe ----------
    # base_options le dice a MediaPipe dónde está el archivo del modelo
    # entrenado (gesture_recognizer.task) que ya sabe reconocer gestos
    # como puño cerrado, mano abierta, pulgar arriba, etc.
    base_options = python.BaseOptions(model_asset_path=MODEL_PATH)

    options = vision.GestureRecognizerOptions(
        base_options=base_options,
        num_hands=1,                        # Solo nos interesa reconocer 1 mano a la vez
        min_hand_detection_confidence=0.5,  # Qué tan seguro debe estar el modelo de que SÍ hay una mano
        min_hand_presence_confidence=0.5,   # Qué tan seguro debe estar de que la mano sigue presente
        min_tracking_confidence=0.5,        # Qué tan seguro debe estar al seguir la mano entre frames
    )
    recognizer = vision.GestureRecognizer.create_from_options(options)

    # ---------- 2) Conexión serial con el ESP32 ----------
    ser = conectar_esp32(SERIAL_PORT, BAUD_RATE)

    # ---------- 3) Captura de video desde la cámara ----------
    cap = cv2.VideoCapture(0)  # El 0 es el índice de la cámara (0 = cámara principal/webcam)
    if not cap.isOpened():
        print("[ERROR] No se pudo abrir la cámara.")
        return

    # Variables para el "debounce": evitan que se manden comandos
    # repetidos todo el tiempo aunque el gesto no haya cambiado.
    last_gesture = None
    last_sent_time = 0.0

    # Variables para el auto-apagado por inactividad
    last_activity_time = time.time()  # última vez que se detectó CUALQUIER gesto válido
    apagado_enviado = False           # evita mandar el comando de apagado repetidamente

    print("Presiona 'q' para salir.")

    # ---------- 4) Bucle principal: se repite mientras la cámara esté abierta ----------
    while cap.isOpened():
        ret, frame = cap.read()  # Captura un frame (una "foto" individual) de la cámara
        if not ret:
            break  # Si no se pudo leer el frame (ej. cámara desconectada), termina el bucle

        # La cámara suele dar la imagen "en espejo"; flip(frame, 1)
        # la voltea horizontalmente para que se vea natural, como
        # si te miraras en un espejo real.
        frame = cv2.flip(frame, 1)

        # MediaPipe espera la imagen en formato RGB, pero OpenCV
        # trabaja internamente en formato BGR (orden de colores
        # invertido). Por eso hay que convertir antes de pasarla al modelo.
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)

        # Aquí es donde MediaPipe analiza la imagen y detecta el gesto
        result = recognizer.recognize(mp_image)

        gesture_name = "None"
        score = 0.0

        if result.gestures:
            # result.gestures[0] es la lista de gestos detectados para
            # la primera mano encontrada, ordenados de mayor a menor
            # confianza. Tomamos el más probable ([0]).
            top = result.gestures[0][0]
            gesture_name = top.category_name  # ej. "Closed_Fist"
            score = top.score                 # ej. 0.94 (94% de confianza)

            now = time.time()
            gesto_cambio = gesture_name != last_gesture
            tiempo_cumplido = (now - last_sent_time) > DEBOUNCE_SECONDS

            # Solo enviamos un comando nuevo si:
            #   (a) el gesto cambió respecto al anterior, O
            #   (b) ya pasó suficiente tiempo (DEBOUNCE_SECONDS) desde
            #       el último envío del mismo gesto.
            # Esto evita saturar el puerto Serial mandando "I30" 30
            # veces por segundo mientras mantienes el puño cerrado.
            if gesture_name in GESTURE_COMMANDS and (gesto_cambio or tiempo_cumplido):
                cmd = GESTURE_COMMANDS[gesture_name]
                if ser is not None:
                    ser.write(cmd.encode())  # .encode() convierte el texto a bytes, que es lo que espera Serial
                print(f"Gesto detectado: {gesture_name} ({score:.2f}) -> Comando: {cmd.strip()}")
                last_gesture = gesture_name
                last_sent_time = now

            # Si el gesto es uno de los válidos, cuenta como "actividad":
            # reiniciamos el reloj de inactividad y permitimos que se
            # pueda volver a apagar más adelante si vuelve a quedar quieto.
            if gesture_name in GESTURE_COMMANDS:
                last_activity_time = now
                apagado_enviado = False

        # ---------- Chequeo de auto-apagado por inactividad ----------
        # Esto corre en CADA frame (haya o no gesto detectado), comparando
        # cuánto tiempo ha pasado desde la última actividad válida.
        now = time.time()
        if (now - last_activity_time) > IDLE_TIMEOUT and not apagado_enviado:
            if ser is not None:
                ser.write(OFF_COMMAND.encode())
            print(f"[INFO] {IDLE_TIMEOUT:.0f}s sin gestos -> Enviando apagado ({OFF_COMMAND.strip()})")
            apagado_enviado = True  # evita reenviar el apagado en cada frame siguiente

        # ---------- 5) Dibujar los puntos de la mano sobre la imagen (opcional, solo visual) ----------
        if result.hand_landmarks:
            h, w, _ = frame.shape
            for hand_landmarks in result.hand_landmarks:
                for lm in hand_landmarks:
                    # Los landmarks vienen normalizados (0.0 a 1.0),
                    # hay que multiplicarlos por el ancho/alto real
                    # de la imagen para saber en qué píxel dibujarlos.
                    cx, cy = int(lm.x * w), int(lm.y * h)
                    cv2.circle(frame, (cx, cy), 4, (0, 255, 0), -1)

        # ---------- 6) Mostrar texto informativo en pantalla ----------
        etiqueta = GESTURE_LABELS_ES.get(gesture_name, gesture_name)
        cv2.putText(frame, f"Gesto: {etiqueta}", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)
        cv2.putText(frame, f"Confianza: {score:.2f}", (10, 60),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)

        # Texto extra: segundos restantes antes del auto-apagado (opcional, solo visual)
        segundos_restantes = max(0.0, IDLE_TIMEOUT - (now - last_activity_time))
        cv2.putText(frame, f"Auto-apagado en: {segundos_restantes:.1f}s", (10, 90),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 200, 255), 2)

        cv2.imshow("Control de Iluminacion por Gestos - UMNG", frame)

        # waitKey(1) espera 1 milisegundo por una tecla; si es 'q', se sale del bucle.
        # Es necesario para que la ventana de video se actualice correctamente.
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    # ---------- 7) Liberar recursos al terminar ----------
    cap.release()          # Libera la cámara para que otros programas puedan usarla
    cv2.destroyAllWindows()  # Cierra la ventana de video
    if ser is not None:
        ser.close()         # Cierra el puerto Serial correctamente


if __name__ == "__main__":
    main()