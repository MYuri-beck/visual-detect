/**
 * pico2w_hid_controller.ino
 *
 * Firmware para Raspberry Pi Pico 2W (RP2350).
 * Emula um teclado HID via USB para controlar a interface
 * do VisualDetect (ui.py) rodando no Raspberry Pi 4.
 *
 * REQUISITO: Arduino IDE com o core "arduino-pico" instalado.
 *   Board Manager URL:
 *   https://github.com/earlephilhower/arduino-pico/releases/download/global/package_rp2040_index.json
 *   Board selecionada: "Raspberry Pi Pico 2 W"
 *
 * Conexao: Pico 2W --USB--> Raspberry Pi 4
 *
 * --- Relacao Pinos GPIO / Tecla ---
 *  GPIO 5  - Seta Direita  -> Right  (proximo botao / proxima imagem)
 *  GPIO 6  - Seta Esquerda -> Left   (botao anterior / voltar)
 *  GPIO 7  - Seta Cima     -> Up     (aumentar valor / navegar para cima)
 *  GPIO 8  - Seta Baixo    -> Down   (diminuir valor / navegar para baixo)
 *  GPIO 9  - Enter         -> Return (confirmar / abrir)
 *
 * Todos os pinos usam INPUT_PULLUP -- conecte o botao entre GPIO e GND.
 *
 * Teclas mapeadas para o VisualDetect (ui.py):
 *   T1  Splash   : Up/Down seleciona INICIAR/GALERIA, ENTER confirma
 *   T2  Config   : Up/Down ajusta valor, ENTER avanca, Left volta
 *   T3  Revisao  : Left/Right seleciona VOLTAR/INICIAR, ENTER confirma
 *   T5  Concluido: Left/Right seleciona NOVO/GALERIA, ENTER confirma
 *   Gal Galeria  : Up/Down navega, ENTER abre, Left volta
 */

#include <Keyboard.h>

// ---------------------------------------------------------------------------
// Configuracao dos botoes
// ---------------------------------------------------------------------------
const uint8_t BUTTONS[]   = { 5, 6, 7, 8, 9 };
const int     NUM_BUTTONS = 5;

// Teclas HID correspondentes (codigos da lib Keyboard do arduino-pico)
const uint8_t KEYS[] = {
  KEY_RIGHT_ARROW,   // GPIO 5 -> Right
  KEY_LEFT_ARROW,    // GPIO 6 -> Left
  KEY_UP_ARROW,      // GPIO 7 -> Up
  KEY_DOWN_ARROW,    // GPIO 8 -> Down
  KEY_RETURN         // GPIO 9 -> Enter
};

// Nomes para debug via Serial
const char* BUTTON_NAMES[] = {
  "Seta Direita (Right)",
  "Seta Esquerda (Left)",
  "Seta Cima    (Up)",
  "Seta Baixo   (Down)",
  "Enter        (Return)"
};

// ---------------------------------------------------------------------------
// Debounce
// ---------------------------------------------------------------------------
// Tempo minimo (ms) entre reconhecimentos do mesmo botao
const unsigned long DEBOUNCE_MS = 30;

bool          lastState[NUM_BUTTONS];
unsigned long lastDebounce[NUM_BUTTONS];

// ---------------------------------------------------------------------------
// Setup
// ---------------------------------------------------------------------------
void setup() {
  Serial.begin(115200);

  // Inicializa todos os pinos como entrada com pull-up interno.
  // O botao deve ser ligado entre o pino e o GND.
  for (int i = 0; i < NUM_BUTTONS; i++) {
    pinMode(BUTTONS[i], INPUT_PULLUP);
    lastState[i]    = HIGH;   // sem pressao = HIGH (pull-up)
    lastDebounce[i] = 0;
  }

  // Inicia o HID Keyboard. No arduino-pico, o USB sobe automaticamente.
  Keyboard.begin();

  Serial.println("=== Pico 2W HID Controller ===");
  Serial.println("Aguardando pressao de botoes...");
}

// ---------------------------------------------------------------------------
// Loop principal
// ---------------------------------------------------------------------------
void loop() {
  unsigned long now = millis();

  for (int i = 0; i < NUM_BUTTONS; i++) {
    bool currentState = digitalRead(BUTTONS[i]);

    // Detecta borda de descida (HIGH -> LOW) com debounce por tempo
    if (currentState == LOW && lastState[i] == HIGH) {
      if ((now - lastDebounce[i]) >= DEBOUNCE_MS) {
        lastDebounce[i] = now;

        Serial.print("[HID] Botao GPIO ");
        Serial.print(BUTTONS[i]);
        Serial.print(" -> ");
        Serial.println(BUTTON_NAMES[i]);

        // Pressiona e solta a tecla (pulso curto, sem repeat automatico)
        Keyboard.press(KEYS[i]);
        delay(15);
        Keyboard.release(KEYS[i]);
      }
    }

    lastState[i] = currentState;
  }

  delay(5);
}
