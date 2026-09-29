<div align="center">

![Header](https://capsule-render.vercel.app/api?type=waving&color=0:2C5364,50:203A43,100:0F2027&height=220&section=header&text=Control%20de%20LEDs%20con%20MediaPipe&fontSize=44&fontColor=ffffff&animation=fadeIn&fontAlignY=38&desc=Iluminación%20por%20gestos%20de%20la%20mano&descAlignY=58&descSize=18)

*Ingeniería Mecatrónica · Universidad Militar Nueva Granada*

<img src="https://readme-typing-svg.demolab.com?font=Fira+Code&size=20&duration=3000&pause=800&color=3AAFFF&center=true&vCenter=true&width=560&lines=%22Pu%C3%B1o+cerrado+%E2%86%92+30%25%22;%22Victoria+%E2%86%92+70%25%22;%22Mano+abierta+%E2%86%92+100%25%22;%22Pulgar+arriba+%E2%86%92+respiraci%C3%B3n%22" alt="Typing SVG" />

<br/>

![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)
![OpenCV](https://img.shields.io/badge/OpenCV-Visión-5C3EE8?style=for-the-badge&logo=opencv&logoColor=white)
![MediaPipe](https://img.shields.io/badge/MediaPipe-Gesture%20Recognizer-0097A7?style=for-the-badge&logo=google&logoColor=white)
![ESP32](https://img.shields.io/badge/ESP32-Arduino-E7352C?style=for-the-badge&logo=espressif&logoColor=white)
![Status](https://img.shields.io/badge/estado-académico-6E40C9?style=for-the-badge)

</div>

<img src="https://capsule-render.vercel.app/api?type=rect&color=0:0F2027,100:203A43&height=3&section=header" width="100%"/>

## ✨ ¿Qué hace este proyecto?

Un sistema en **Python** que controla la intensidad de un 💡 **LED** a partir de los
**gestos de tu mano**, detectados en tiempo real con la cámara web. Es un proyecto
básico para aprender y familiarizarse con **MediaPipe**.

<div align="center">

| 📷 Cámara | 🖐️ MediaPipe | 🔌 Serie (USB) | 💡 ESP32 |
|:---:|:---:|:---:|:---:|
| Captura cada frame | Reconoce el gesto de la mano | Envía comandos ya decididos | Genera la señal PWM del LED |

</div>

<img src="https://capsule-render.vercel.app/api?type=rect&color=0:0F2027,100:203A43&height=3&section=header" width="100%"/>

## 🖐️ Gestos y comportamiento del LED

<div align="center">

| Gesto | Nombre en MediaPipe | Comando | Comportamiento |
|:---:|:---|:---:|:---|
| ✊ | `Closed_Fist` | `I30` | Intensidad al **30 %** |
| ✌️ | `Victory` | `I70` | Intensidad al **70 %** |
| 🖐️ | `Open_Palm` | `I100` | Intensidad al **100 %** |
| 👎 | `Thumb_Down` | `M1` | **Modo 1:** parpadeo (5 destellos) |
| 👍 | `Thumb_Up` | `M2` | **Modo 2:** respiración (*fade in / fade out*) |
| ⏱️ | Sin gesto por 3 s | `I0` | **Auto-apagado** del LED |

</div>

> 💡 Los modos 1 y 2 funcionan como "interrupciones de software": interrumpen el control
> normal de intensidad para ejecutar una secuencia. No son interrupciones de hardware
> (timers o pines externos).

<img src="https://capsule-render.vercel.app/api?type=rect&color=0:0F2027,100:203A43&height=3&section=header" width="100%"/>

## 📸 Capturas

<div align="center">

<table>
  <tr>
    <td align="center">
      <img src="docs/im%C3%A1genes/Circuito%20Fisico.jpeg" width="480"/><br/>
      <sub>Montaje físico: ESP32, resistencia y LED</sub>
    </td>
    <td align="center">
      <img src="docs/im%C3%A1genes/Prueba%20Pu%C3%B1o%20Cerrado.jpeg" width="480"/><br/>
      <sub>Puño cerrado → 30 %</sub>
    </td>
  </tr>
  <tr>
    <td align="center">
      <img src="docs/im%C3%A1genes/Prueba%20Mano%20Paz.jpeg" width="480"/><br/>
      <sub>Victoria → 70 %</sub>
    </td>
    <td align="center">
      <img src="docs/im%C3%A1genes/Prueba%20Mano%20Abierta.jpeg" width="480"/><br/>
      <sub>Mano abierta → 100 %</sub>
    </td>
  </tr>
  <tr>
    <td align="center">
      <img src="docs/im%C3%A1genes/Modo%201%20Pulgar%20Abajo.jpeg" width="480"/><br/>
      <sub>Pulgar abajo → Modo 1 (parpadeo)</sub>
    </td>
    <td align="center">
      <img src="docs/im%C3%A1genes/Modo%202%20Pulgar%20Arriba.jpeg" width="480"/><br/>
      <sub>Pulgar arriba → Modo 2 (respiración)</sub>
    </td>
  </tr>
</table>

</div>

<img src="https://capsule-render.vercel.app/api?type=rect&color=0:0F2027,100:203A43&height=3&section=header" width="100%"/>

## 🎥 Video de funcionamiento

> GitHub no reproduce videos `.mp4` alojados en el repo directamente dentro del README,
> así que se deja como enlace descargable/reproducible desde el navegador.

- ▶️ [**Funcionamiento del sistema**](docs/videos/Video%20Funcionamiento.mp4) — demo completa del control de LEDs por gestos.

<div align="center">

**GIF de funcionamiento** — vista rápida del control del LED por gestos en acción:

<img src="docs/videos/GIF%20FUNCIONAMIENTO.gif" width="560" alt="GIF de funcionamiento" />

</div>

<img src="https://capsule-render.vercel.app/api?type=rect&color=0:0F2027,100:203A43&height=3&section=header" width="100%"/>

## 📐 Arquitectura general

```
📷  Cámara web
        │  frames
        ▼
┌──────────────────────────────┐
│   gesture_control.py  (PC)   │
│                              │
│  1️⃣  OpenCV captura, voltea  │
│      y convierte BGR → RGB   │
│                              │
│  2️⃣  MediaPipe reconoce el   │
│      gesto de la mano        │
│                              │
│  3️⃣  Se busca el comando     │
│      asociado al gesto       │
└──────────────┬───────────────┘
               │ Puerto serie (USB) — ej. "I30\n"
               ▼
┌──────────────────────────────┐
│           ESP32              │
│      (esp32_firmware.ino)    │
│  procesarComando()           │
│  ledcWrite() → PWM en GPIO 2 │
└──────────────┬───────────────┘
               ▼
              💡 LED
```

> 💡 **Idea clave:** la ESP32 **no reconoce gestos**. Toda la visión artificial vive en la
> PC. La ESP32 solo recibe comandos ya decididos y simples (`"I30"`, `"M1"`) por cable USB
> y genera la señal PWM del LED.

<img src="https://capsule-render.vercel.app/api?type=rect&color=0:0F2027,100:203A43&height=3&section=header" width="100%"/>

## 📁 Estructura del repositorio

```
Manejo-leds-mediante-el-uso-de-MediaPipe/
├── gesture_control.py          # Programa principal en Python (PC)
├── gesture_recognizer.task     # Modelo preentrenado de MediaPipe
├── esp32_firmware/
│   └── esp32_firmware.ino      # Firmware del ESP32
├── docs/                       # Capturas y video de demostración
│   ├── imágenes/
│   │   ├── Circuito Fisico.jpeg
│   │   ├── Prueba Puño Cerrado.jpeg
│   │   ├── Prueba Mano Paz.jpeg
│   │   ├── Prueba Mano Abierta.jpeg
│   │   ├── Modo 1 Pulgar Abajo.jpeg
│   │   └── Modo 2 Pulgar Arriba.jpeg
│   └── videos/
│       ├── Video Funcionamiento.mp4
│       └── GIF FUNCIONAMIENTO.gif
└── README.md
```

<img src="https://capsule-render.vercel.app/api?type=rect&color=0:0F2027,100:203A43&height=3&section=header" width="100%"/>

## ⚙️ Requisitos

<div align="center">
<img src="https://skillicons.dev/icons?i=python,opencv,arduino,cpp&theme=dark" />
</div>

- ✅ Python 3.10+
- ✅ Una cámara web
- ✅ Un ESP32 con:
  - LED 💡 → resistencia (220 Ω – 330 Ω) → **GPIO 2**
  - Cátodo del LED → GND
- ✅ Arduino IDE con el paquete **esp32 by Espressif Systems v3.x**
- ✅ Cable USB para conectar la ESP32 a la PC

```
GPIO 2 ──▶ Resistencia (220–330 Ω) ──▶ LED (ánodo +) ──▶ LED (cátodo −) ──▶ GND
```

**Instalar dependencias de Python:**

```bash
pip install opencv-python mediapipe pyserial
```

> ⚠️ El firmware usa la API de PWM de la versión **3.x** del paquete ESP32
> (`ledcAttach()` y `ledcWrite(PIN, duty)`). Con la versión 2.x, basada en canales
> (`ledcSetup()` + `ledcAttachPin()`), no compilará.

<img src="https://capsule-render.vercel.app/api?type=rect&color=0:0F2027,100:203A43&height=3&section=header" width="100%"/>

## ▶️ Cómo correrlo

1. **Sube** `esp32_firmware/esp32_firmware.ino` a la ESP32 desde Arduino IDE.
2. **Cierra el Monitor Serial** del Arduino IDE (ocupa el puerto).
3. **Anota el puerto** (`COM3` en Windows, `/dev/ttyUSB0` en Linux/Mac) y ajústalo en `gesture_control.py`:
   ```python
   SERIAL_PORT = "COM3"
   ```
4. **Corre** el programa desde la carpeta raíz del repositorio:
   ```bash
   python gesture_control.py
   ```
5. Realiza los gestos frente a la cámara:

   | Acción | Cómo |
   |:---|:---|
   | 🖐️ Controlar el LED | Haz uno de los 5 gestos frente a la cámara |
   | ⏱️ Auto-apagado | Quita la mano por 3 segundos |
   | 🚪 Salir | Presiona `q` en la ventana de video |

> El script imprime al iniciar los puertos seriales detectados, para ayudarte a elegir el
> correcto. Si la ESP32 no está conectada, el programa sigue funcionando solo con la parte
> de visión, sin enviar comandos.

### 🔧 Parámetros configurables

| Variable | Valor | Descripción |
|:---|:---:|:---|
| `MODEL_PATH` | `gesture_recognizer.task` | Ruta del modelo de MediaPipe |
| `SERIAL_PORT` | `COM3` | Puerto serie de la ESP32 |
| `BAUD_RATE` | `115200` | Velocidad serie (igual que en el firmware) |
| `DEBOUNCE_SECONDS` | `1.0` | Tiempo mínimo entre envíos del mismo gesto |
| `IDLE_TIMEOUT` | `3.0` | Segundos sin gestos antes de apagar el LED |

<img src="https://capsule-render.vercel.app/api?type=rect&color=0:0F2027,100:203A43&height=3&section=header" width="100%"/>

## 📡 Protocolo de comunicación

Texto plano terminado en salto de línea (`\n`). El firmware usa
`Serial.readStringUntil('\n')`, por eso el terminador es obligatorio.

<div align="center">

| Comando | Acción |
|:---:|:---|
| `I<0-100>` | Fija la intensidad del LED (se limita al rango 0–100 %) |
| `M1` | Ejecuta la secuencia del Modo 1 (parpadeo) |
| `M2` | Ejecuta la secuencia del Modo 2 (respiración) |

</div>

<img src="https://capsule-render.vercel.app/api?type=rect&color=0:0F2027,100:203A43&height=3&section=header" width="100%"/>

## 🧩 Explicación del código, bloque por bloque

### 1️⃣ `gesture_control.py` — el programa principal

<details>
<summary><b>🧠 Inicialización del Gesture Recognizer</b></summary>

```python
base_options = python.BaseOptions(model_asset_path=MODEL_PATH)
options = vision.GestureRecognizerOptions(
    base_options=base_options,
    num_hands=1,
    min_hand_detection_confidence=0.5,
    min_hand_presence_confidence=0.5,
    min_tracking_confidence=0.5,
)
recognizer = vision.GestureRecognizer.create_from_options(options)
```

Carga el modelo preentrenado `gesture_recognizer.task` y configura el reconocedor.
`num_hands=1` limita la detección a una sola mano, y los tres umbrales de confianza (0.5)
definen qué tan seguro debe estar el modelo de que hay una mano, de que sigue presente y
de que la está siguiendo bien entre frames.

</details>

<details>
<summary><b>🔌 Conexión serie con la ESP32</b></summary>

```python
ser = serial.Serial(puerto, baud, timeout=1)
time.sleep(2)
```

Abre el puerto USB donde está la ESP32. Si falla (placa desconectada, puerto incorrecto),
el programa **sigue funcionando** solo con visión y avisa que no enviará comandos.

El `time.sleep(2)` es necesario porque la ESP32 **se reinicia automáticamente** cuando la PC
abre el puerto serie; el retardo le da tiempo de arrancar antes de recibir el primer comando.

</details>

<details>
<summary><b>📷 Captura y preparación del frame</b></summary>

```python
ret, frame = cap.read()
frame = cv2.flip(frame, 1)
rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
```

- `cv2.flip(frame, 1)` voltea la imagen horizontalmente para que se vea como un espejo.
- `cvtColor(BGR → RGB)` es obligatorio: OpenCV trabaja internamente en **BGR**, pero
  MediaPipe espera **RGB**. Sin esta conversión, los colores quedan invertidos y el
  reconocimiento empeora.

</details>

<details>
<summary><b>🖐️ Reconocimiento del gesto</b></summary>

```python
result = recognizer.recognize(mp_image)
if result.gestures:
    top = result.gestures[0][0]
    gesture_name = top.category_name   # ej. "Closed_Fist"
    score = top.score                  # ej. 0.94
```

MediaPipe devuelve, para cada mano detectada, una lista de gestos ordenados de mayor a menor
confianza. Se toma el más probable (`[0][0]`) junto con su `score` (de 0 a 1).

</details>

<details>
<summary><b>⏲️ Debounce: no saturar el puerto serie</b></summary>

```python
gesto_cambio = gesture_name != last_gesture
tiempo_cumplido = (now - last_sent_time) > DEBOUNCE_SECONDS

if gesture_name in GESTURE_COMMANDS and (gesto_cambio or tiempo_cumplido):
    ser.write(cmd.encode())
```

Solo se envía un comando si el gesto **cambió** o si ya pasó `DEBOUNCE_SECONDS` desde el
último envío. Sin esto, mantener el puño cerrado mandaría `"I30"` unas 30 veces por segundo.

</details>

<details>
<summary><b>🗺️ Mapeo gesto → comando</b></summary>

```python
GESTURE_COMMANDS = {
    "Closed_Fist": "I30\n",
    "Victory":     "I70\n",
    "Open_Palm":   "I100\n",
    "Thumb_Down":  "M1\n",
    "Thumb_Up":    "M2\n",
}
```

Un diccionario simple que traduce el nombre del gesto al texto que entiende la ESP32.
El `"\n"` final marca dónde termina cada comando.

</details>

<details>
<summary><b>😴 Auto-apagado por inactividad</b></summary>

```python
if (now - last_activity_time) > IDLE_TIMEOUT and not apagado_enviado:
    ser.write(OFF_COMMAND.encode())
    apagado_enviado = True
```

Cada vez que se detecta un gesto válido se reinicia `last_activity_time`. Si pasan
`IDLE_TIMEOUT` segundos sin actividad, se envía `"I0"` **una sola vez** (la bandera
`apagado_enviado` evita repetirlo en cada frame).

</details>

<details>
<summary><b>🔁 El loop principal y la liberación de recursos</b></summary>

```python
while cap.isOpened():
    ...
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()
ser.close()
```

Repite: captura → reconoce → envía → dibuja el resultado en pantalla. Al presionar `q`
sale del bucle y libera la cámara, cierra la ventana y cierra el puerto serie.

</details>

### 2️⃣ `esp32_firmware.ino` — firmware del ESP32

> 🧠 **Filosofía del sketch:** este programa **no reconoce gestos**, solo obedece
> comandos y genera la señal PWM del LED.

<details>
<summary><b>⚙️ Configuración del PWM en <code>setup()</code></b></summary>

```cpp
const int PWM_FREQ = 5000;
const int PWM_RESOLUTION = 8;

ledcAttach(LED_PIN, PWM_FREQ, PWM_RESOLUTION);
ledcWrite(LED_PIN, 0);
```

Configura el hardware **LEDC** de la ESP32: en `LED_PIN` (GPIO 2) se genera una señal PWM
de **5 kHz** con **8 bits** de resolución (duty cycle de 0 a 255). El LED arranca apagado.

</details>

<details>
<summary><b>💡 Fijar la intensidad</b></summary>

```cpp
void setIntensity(int percent) {
  percent = constrain(percent, 0, 100);
  int duty = map(percent, 0, 100, 0, 255);
  ledcWrite(LED_PIN, duty);
}
```

Convierte un porcentaje "humano" (0–100 %) en un duty cycle de hardware (0–255):
30 % ≈ 76, 70 % ≈ 178, 100 % = 255. `constrain()` protege contra valores fuera de rango.

</details>

<details>
<summary><b>👎 Modo 1: parpadeo</b></summary>

```cpp
for (int i = 0; i < 5; i++) {
  ledcWrite(LED_PIN, 255);
  delay(150);
  ledcWrite(LED_PIN, 0);
  delay(150);
}
```

Enciende y apaga el LED 5 veces con 150 ms entre cada cambio.

</details>

<details>
<summary><b>👍 Modo 2: respiración (fade)</b></summary>

```cpp
for (int duty = 0; duty <= 255; duty += 5) { ledcWrite(LED_PIN, duty); delay(15); }
for (int duty = 255; duty >= 0; duty -= 5) { ledcWrite(LED_PIN, duty); delay(15); }
```

Sube el duty cycle de 0 a 255 y luego lo baja de vuelta a 0, en pasos de 5 con 15 ms de
espera. Aquí es donde más se nota la ventaja del PWM: el brillo cambia de forma suave, como
si el LED "respirara".

</details>

<details>
<summary><b>✅ Interpretar el comando recibido</b></summary>

```cpp
void loop() {
  if (Serial.available() > 0) {
    String comando = Serial.readStringUntil('\n');
    procesarComando(comando);
  }
}

void procesarComando(String comando) {
  comando.trim();
  if (comando.startsWith("I")) { setIntensity(comando.substring(1).toInt()); }
  else if (comando == "M1")    { modo1_secuencia(); }
  else if (comando == "M2")    { modo2_secuencia(); }
}
```

`loop()` revisa si llegó algo por el puerto serie; si es así, lee hasta el `\n` y se lo pasa
a `procesarComando()`. Los comandos que empiezan por `I` extraen el número que sigue y lo
usan como intensidad; `M1` y `M2` lanzan las secuencias.

</details>

<img src="https://capsule-render.vercel.app/api?type=rect&color=0:0F2027,100:203A43&height=3&section=header" width="100%"/>

## 🧠 Conceptos clave

<details>
<summary><b>🖐️ MediaPipe Gesture Recognizer</b></summary>

Solución de Google que, a partir de una imagen, detecta la mano, ubica **21 puntos de
referencia** (*landmarks*) y clasifica el gesto (puño cerrado, mano abierta, pulgar arriba,
etc.). Aquí se usa el **modelo preentrenado** que ofrece Google (`gesture_recognizer.task`);
no se entrenó un modelo propio.

</details>

<details>
<summary><b>🎨 BGR vs RGB</b></summary>

Dos formas de ordenar los canales de color de una imagen. OpenCV usa **BGR** (azul, verde,
rojo) y MediaPipe espera **RGB**. Por eso hay que convertir cada frame antes de analizarlo.

</details>

<details>
<summary><b>⚡ PWM (Modulación por Ancho de Pulso)</b></summary>

Un pin digital solo puede estar en 3.3 V o en 0 V. Para simular "media intensidad", el
pin se enciende y apaga miles de veces por segundo; el ojo humano no percibe el parpadeo y
ve un **brillo promedio**. Lo que cambia no es el voltaje, sino **cuánto tiempo del ciclo**
está encendido.

</details>

<details>
<summary><b>📊 Duty cycle (ciclo de trabajo)</b></summary>

Porcentaje del ciclo en que la señal PWM está en alto. 100 % = siempre encendido (máximo
brillo), 50 % = encendido la mitad del tiempo, 0 % = apagado. Con 8 bits de resolución se
representa con un número de 0 a 255.

</details>

<details>
<summary><b>🔌 Comunicación serie (UART/USB)</b></summary>

Forma simple de que una PC y un microcontrolador se hablen: un cable USB por el que viajan
bytes, línea por línea. Aquí la PC envía texto (`"I30\n"`) y la ESP32 lo lee con
`Serial.readStringUntil('\n')`.

</details>

<details>
<summary><b>⚡ Baudios</b></summary>

Velocidad a la que viajan los datos por el puerto serie (aquí, **115200**). La PC y la ESP32
deben usar el mismo valor, o los datos llegarán corruptos.

</details>

<details>
<summary><b>⏲️ Debounce</b></summary>

Técnica para evitar que una misma señal se procese muchas veces seguidas. Aquí limita el
envío repetido del mismo gesto a uno por segundo.

</details>

<details>
<summary><b>📌 GPIO (General Purpose Input/Output)</b></summary>

Pines del microcontrolador programables para entregar o leer una señal eléctrica. Aquí el
**GPIO 2** entrega la señal PWM al LED.

</details>

<img src="https://capsule-render.vercel.app/api?type=rect&color=0:0F2027,100:203A43&height=3&section=header" width="100%"/>

## 🛠️ Solución de problemas

| Problema | Posible solución |
|:---|:---|
| `ModuleNotFoundError` (`cv2`, `mediapipe`, `serial`) | Ejecuta `pip install opencv-python mediapipe pyserial` |
| No se encuentra `gesture_recognizer.task` | Ejecuta el script desde la carpeta raíz del repositorio |
| `was not declared in this scope` con `ledcAttach` | Actualiza el paquete de placas ESP32 a la versión 3.x |
| No se pudo conectar al ESP32 | Verifica `SERIAL_PORT` y cierra el Monitor Serial del Arduino IDE |
| No abre la cámara | Prueba otro índice en `cv2.VideoCapture(0)` o cierra otras apps que la usen |
| El gesto no se detecta bien | Mejora la iluminación y mantén la mano completa dentro del encuadre |

<img src="https://capsule-render.vercel.app/api?type=rect&color=0:0F2027,100:203A43&height=3&section=header" width="100%"/>

## 🔒 Nota de privacidad

> El reconocimiento de gestos se ejecuta **localmente** en tu computador con el modelo
> `gesture_recognizer.task`: las imágenes de la cámara **no se envían a ningún servidor**.

<div align="center">

## 👤 Autor

**Julián** · Ingeniería Mecatrónica · Universidad Militar Nueva Granada

![Footer](https://capsule-render.vercel.app/api?type=waving&color=0:0F2027,50:203A43,100:2C5364&height=120&section=footer)

</div>
