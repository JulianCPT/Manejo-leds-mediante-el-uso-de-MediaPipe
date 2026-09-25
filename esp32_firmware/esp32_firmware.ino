/*
  Sistema de control de iluminación basado en gestos de mano
  Universidad Militar Nueva Granada - Ingeniería Mecatrónica

  Firmware para ESP32. Recibe comandos por Serial (USB) enviados
  desde el script de Python (gesture_control.py) y controla la
  intensidad de un LED mediante PWM, además de ejecutar dos
  secuencias especiales (Modo 1 / Modo 2) activadas por interrupción
  de software (gestos de pulgar arriba/abajo).

  Protocolo de comandos (texto + salto de línea '\n'):
    "I30"   -> Fijar intensidad al 30%
    "I70"   -> Fijar intensidad al 70%
    "I100"  -> Fijar intensidad al 100%
    "M1"    -> Ejecutar secuencia Modo 1 (Thumb_Down)
    "M2"    -> Ejecutar secuencia Modo 2 (Thumb_Up)
*/

// ============================================================
//  ¿QUÉ ES PWM Y POR QUÉ LO USAMOS?
// ============================================================
// El ESP32 (como casi todos los microcontroladores) SOLO puede
// poner un pin digital en dos estados: ENCENDIDO (3.3V) o
// APAGADO (0V). No existe un pin que entregue "50% de voltaje"
// de forma continua.
//
// Entonces, ¿cómo se logra que un LED se vea "a media intensidad"?
// Con un truco: encender y apagar el LED MUY RÁPIDO (miles de
// veces por segundo). El ojo humano no alcanza a percibir ese
// parpadeo y en cambio percibe un brillo promedio.
//
// A esta técnica se le llama PWM (Pulse Width Modulation =
// Modulación por Ancho de Pulso). La palabra clave es "ancho de
// pulso": lo que cambia no es el voltaje, sino CUÁNTO TIEMPO,
// dentro de cada ciclo, el pin está en ENCENDIDO vs APAGADO.
//
// A ese porcentaje de tiempo encendido se le llama "duty cycle"
// (ciclo de trabajo). Ejemplos:
//   - Duty cycle 100% -> el pin está siempre encendido -> LED al máximo brillo
//   - Duty cycle 50%  -> encendido la mitad del tiempo  -> se ve a media intensidad
//   - Duty cycle 0%   -> siempre apagado                -> LED apagado
//
// El ESP32 tiene hardware dedicado (llamado "LEDC", LED Controller)
// que genera esta señal PWM automáticamente por nosotros, sin que
// tengamos que estar prendiendo y apagando el pin manualmente con
// delay() (eso sería muy lento e impreciso). Nosotros solo le
// decimos: "en este pin, quiero una señal PWM con esta frecuencia,
// esta resolución, y este duty cycle" y el ESP32 se encarga del resto.
// ============================================================

#define LED_PIN 2          // Pin GPIO del ESP32 donde está conectado el LED (a través de su resistencia)

// --- Configuración del PWM (hardware LEDC del ESP32) ---
// NOTA DE COMPATIBILIDAD: existen dos versiones de la librería del
// ESP32 para Arduino con APIs distintas para manejar PWM:
//   - Paquete de placas ESP32 v2.x (más antiguo): usa ledcSetup() +
//     ledcAttachPin() + un número de "canal" (0-15) separado del pin.
//   - Paquete de placas ESP32 v3.x (más reciente, el que tienes tú):
//     usa ledcAttach() directamente sobre el PIN, sin manejar canales
//     a mano (la librería los asigna internamente). Es más simple.
// Este código usa la API NUEVA (v3.x). Si te vuelve a salir un error
// de "was not declared in this scope", revisa en Arduino IDE > Tools
// > Board Manager qué versión de "esp32 by Espressif Systems" tienes
// instalada.

// Frecuencia de la señal PWM, en Hz (ciclos por segundo).
// 5000 Hz significa que el ciclo completo (encendido+apagado) se
// repite 5000 veces por segundo. Es mucho más rápido de lo que el
// ojo humano puede detectar (por eso no se ve parpadear), pero no
// tan alta como para causar problemas eléctricos. Para LEDs, un
// rango típico es 1 kHz - 5 kHz.
const int PWM_FREQ = 5000; // 5 kHz

// Resolución en bits: define cuántos "escalones" de duty cycle
// existen entre 0% y 100%.
// Con 8 bits, el duty cycle se representa con un número de 0 a 255
// (2^8 = 256 valores posibles):
//   0   = 0% (apagado)
//   128 = ~50%
//   255 = 100% (máximo brillo)
// A más bits de resolución, más "escalones" de brillo intermedios,
// pero también más lenta puede ser la señal a la misma frecuencia.
// 8 bits es más que suficiente para que el ojo humano perciba una
// transición de brillo suave.
const int PWM_RESOLUTION = 8;

volatile bool interrupcionActiva = false; // Bandera para saber si estamos ejecutando una secuencia especial (Modo 1/2)

void setup() {
  Serial.begin(115200); // Inicia la comunicación serial (debe coincidir con BAUD_RATE en el script de Python)
  delay(500);

  // --- Configuración del hardware PWM (se hace UNA sola vez, aquí en setup) ---

  // ledcAttach: le decimos al ESP32 "en este pin (LED_PIN), genera una
  // señal PWM con esta frecuencia y esta resolución". La librería se
  // encarga internamente de asignar un canal de hardware disponible;
  // nosotros ya no necesitamos manejar el número de canal a mano.
  ledcAttach(LED_PIN, PWM_FREQ, PWM_RESOLUTION);

  // Empezamos con el LED apagado (duty cycle = 0).
  // Nota: en la API nueva, ledcWrite() recibe el PIN, no un canal.
  ledcWrite(LED_PIN, 0);

  Serial.println("ESP32 listo. Esperando comandos...");
}

// Convierte un porcentaje "humano" (0-100%) en un valor de duty
// cycle "de hardware" (0-255, porque usamos 8 bits de resolución)
// y se lo entrega al canal PWM.
void setIntensity(int percent) {
  // constrain() evita valores fuera de rango si llega un dato inválido
  // (ej. si por error llegara "I150", lo recorta a 100)
  percent = constrain(percent, 0, 100);

  // map() hace una "regla de tres" simple:
  //   percent  está en el rango [0, 100]
  //   duty     debe quedar en el rango [0, 255]
  // Ejemplo: 30% -> duty = 0.30 * 255 ≈ 76
  //          70% -> duty = 0.70 * 255 ≈ 178
  //          100% -> duty = 255
  int duty = map(percent, 0, 100, 0, 255);

  // Aquí es donde realmente se actualiza la señal física en el pin.
  // El ESP32 empieza a generar, en LED_PIN, pulsos con ese nuevo
  // duty cycle a 5000 Hz, de forma automática y continua (no hay
  // que volver a llamar esta función a menos que quieras cambiar
  // la intensidad de nuevo).
  ledcWrite(LED_PIN, duty);

  Serial.print("Intensidad establecida: ");
  Serial.print(percent);
  Serial.println("%");
}

// --- Interrupción 1 (gesto Thumb_Down): secuencia de parpadeo rápido ---
// Nota: no es una "interrupción" de hardware real (como un timer o un
// pin externo), sino una función que se dispara cuando llega el
// comando "M1" por Serial. La llamamos así porque conceptualmente
// interrumpe el comportamiento normal (control de intensidad) para
// ejecutar una secuencia especial.
void modo1_secuencia() {
  Serial.println(">> Interrupcion 1 (Thumb_Down): ejecutando Modo 1");
  interrupcionActiva = true;

  // Enciende (duty=255, 100%) y apaga (duty=0, 0%) el LED 5 veces,
  // con 150 ms entre cada cambio -> efecto de parpadeo
  for (int i = 0; i < 5; i++) {
    ledcWrite(LED_PIN, 255);
    delay(150);
    ledcWrite(LED_PIN, 0);
    delay(150);
  }

  interrupcionActiva = false;
  Serial.println(">> Modo 1 finalizado");
}

// --- Interrupción 2 (gesto Thumb_Up): secuencia de "respiración" (fade in/out) ---
// Aquí es donde más se nota la ventaja del PWM: en vez de solo
// encendido/apagado, subimos y bajamos el duty cycle gradualmente
// (de 0 a 255 y de vuelta a 0), lo que se percibe como un brillo
// que sube y baja suavemente, como si el LED "respirara".
void modo2_secuencia() {
  Serial.println(">> Interrupcion 2 (Thumb_Up): ejecutando Modo 2");
  interrupcionActiva = true;

  // Fade in: sube el duty cycle de 0 a 255 de 5 en 5, esperando
  // 15 ms entre cada paso (por eso se ve como una transición suave
  // y no un salto brusco)
  for (int duty = 0; duty <= 255; duty += 5) {
    ledcWrite(LED_PIN, duty);
    delay(15);
  }
  // Fade out: el mismo proceso, pero bajando de 255 a 0
  for (int duty = 255; duty >= 0; duty -= 5) {
    ledcWrite(LED_PIN, duty);
    delay(15);
  }

  interrupcionActiva = false;
  Serial.println(">> Modo 2 finalizado");
}

// Interpreta el texto recibido por Serial y decide qué función llamar.
// Este es el "traductor" entre el protocolo de comandos (texto) y
// las acciones reales del LED.
void procesarComando(String comando) {
  comando.trim(); // Elimina espacios y saltos de línea sobrantes

  if (comando.startsWith("I")) {
    // Comandos tipo "I30", "I70", "I100" -> extraemos el número después de la "I"
    int intensidad = comando.substring(1).toInt();
    setIntensity(intensidad);

  } else if (comando == "M1") {
    modo1_secuencia();

  } else if (comando == "M2") {
    modo2_secuencia();

  } else {
    Serial.print("Comando no reconocido: ");
    Serial.println(comando);
  }
}

// loop() se ejecuta en bucle infinito, todo el tiempo, mientras el
// ESP32 esté encendido. Aquí solo revisamos si llegó algo nuevo por
// el puerto Serial (enviado desde Python) y, si es así, lo procesamos.
void loop() {
  if (Serial.available() > 0) {
    // readStringUntil('\n') lee todo lo que llegó hasta encontrar un
    // salto de línea. Esto coincide con que en Python cada comando
    // se envía terminado en "\n" (ej. "I30\n").
    String comando = Serial.readStringUntil('\n');
    procesarComando(comando);
  }
}
