/**
 * esp32_hid_controller.ino
 *
 * Firmware para ESP32-S2/S3 com suporte USB nativo.
 * Emula um teclado HID via USB para controlar a interface
 * do batch_processor.py rodando no Raspberry Pi 4.
 *
 * Conexão: ESP32 -> USB -> Raspberry Pi 4
 *
 * --- Relação Pinos / Tecla ---
 * Pino 5  - Seta Direita  -> next (próxima imagem)
 * Pino 6  - Seta Esquerda -> back (imagem anterior)
 * Pino 7  - Seta Cima     -> mais (aumentar parâmetro)
 * Pino 8  - Seta Baixo    -> menos (diminuir parâmetro)
 * Pino 9  - Enter         -> confirmar (aceitar/capturar)
 */

#include <USB.h>
#include <USBHIDKeyboard.h>

USBHIDKeyboard Keyboard;

// ---------------------------------------------------------------------------
// Configuração dos botões
// ---------------------------------------------------------------------------
const uint8_t buttons[]    = { 5, 6, 7, 8, 9 };
const int     NUM_BUTTONS  = 5;

const uint16_t keys[] = {
  KEY_RIGHT_ARROW,   // next
  KEY_LEFT_ARROW,    // back
  KEY_UP_ARROW,      // mais
  KEY_DOWN_ARROW,    // menos
  KEY_RETURN         // confirmar
};

// Nomes para debug via Serial (útil no Wokwi e no monitor serial)
const char* buttonNames[] = {
  "Seta Direita (Next)",
  "Seta Esquerda (Back)",
  "Seta Cima (Mais)",
  "Seta Baixo (Menos)",
  "Enter (Confirmar)"
};

// ---------------------------------------------------------------------------
// Estado dos botões (debounce simples por nível)
// ---------------------------------------------------------------------------
bool lastButtonsState[NUM_BUTTONS];

// ---------------------------------------------------------------------------
// Setup
// ---------------------------------------------------------------------------
void setup() {
  Serial.begin(115200);

  for (int i = 0; i < NUM_BUTTONS; i++) {
    pinMode(buttons[i], INPUT_PULLUP);
    lastButtonsState[i] = HIGH;
  }

  Keyboard.begin();
  USB.begin();
}

// ---------------------------------------------------------------------------
// Loop principal
// ---------------------------------------------------------------------------
void loop() {
  for (int i = 0; i < NUM_BUTTONS; i++) {
    bool currentState = digitalRead(buttons[i]);

    if (currentState == LOW && lastButtonsState[i] == HIGH) {
      // Debug serial (visível no Wokwi ou monitor serial)
      Serial.print("Botao pressionado: PINO ");
      Serial.print(buttons[i]);
      Serial.print(" -> Enviando tecla: ");
      Serial.println(buttonNames[i]);

      // Envia o pressionamento HID
      Keyboard.press(keys[i]);
      delay(10);
      Keyboard.release(keys[i]);
    }

    lastButtonsState[i] = currentState;
  }

  delay(10);
}
