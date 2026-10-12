/**
 * @file    TFT_RP2040_GIF_Dimmer.ino
 * @brief   Firmware para RP2040 Zero com display TFT 1.54" ST7789 (240x240)
 *
 * Comportamento:
 *   1. Reproduz um GIF animado em loop com brilho máximo.
 *   2. Gradualmente escurece o backlight (PWM) ao longo de DIM_DURATION_MS.
 *   3. Quando o brilho atinge BRIGHTNESS_MIN, aguarda PAUSE_DARK_MS.
 *   4. Preenche a tela de branco e sobe o brilho ao máximo.
 *   5. Aguarda CAPTURE_HOLD_MS (tempo para o RPi 4 tirar a captura).
 *   6. Volta ao passo 1.
 *
 * @project VisualDetect – Óculos de Estimulação Visual
 *
 * @hardware
 *   MCU    : RP2040 Zero (Waveshare)
 *   Display: TFT 1.54" ST7789  (240 x 240)
 *
 * @pinout
 *   Display  →  RP2040 Zero
 *   GND      →  GND
 *   VCC      →  3.3V
 *   SCL      →  GP2  (SPI0 SCK)
 *   SDA      →  GP3  (SPI0 MOSI)
 *   RES      →  GP4  (RST)
 *   DC       →  GP5
 *   CS       →  GP6
 *   BL       →  GP7  (PWM – controle de brilho)
 *
 * @dependencies (Arduino Library Manager)
 *   - TFT_eSPI    (Bodmer)
 *   - AnimatedGIF (Larry Bank)
 *   - earlephilhower/arduino-pico (board manager)
 *
 * @notes
 *   Copie o User_Setup.h deste projeto para dentro de
 *   libraries/TFT_eSPI/ (sobrescreva o original).
 *   O arquivo gatotft.h deve estar na mesma pasta deste .ino.
 */

#include <Arduino.h>
#include <SPI.h>
#include <TFT_eSPI.h>
#include <AnimatedGIF.h>
#include "gatotft.h"

// ============================================================
// Parâmetros – ajuste conforme necessário
// ============================================================

/** Duração total do efeito de escurecimento (ms) */
#define DIM_DURATION_MS   15000UL

/** Brilho máximo PWM (0–255) */
#define BRIGHTNESS_MAX    255

/** Brilho mínimo que aciona a captura (0–255) */
#define BRIGHTNESS_MIN    5

/** Pausa com tela escura antes da tela branca (ms) */
#define PAUSE_DARK_MS     1500UL

/** Tempo que a tela branca fica acesa para o RPi tirar a foto (ms) */
#define CAPTURE_HOLD_MS   3000UL

// ============================================================
// Dimensões GIF e display
// ============================================================
#define GIF_W   103
#define GIF_H   103
#define DISP_W  240
#define DISP_H  240

// ============================================================
// Objetos e estado global
// ============================================================
TFT_eSPI    tft;
AnimatedGIF gif;

enum State { GIF_PLAYING, DARK_PAUSE, WHITE_CAPTURE };
State    state         = GIF_PLAYING;
uint32_t stateEnterMs  = 0;   // millis() quando entrou no estado atual
bool     gifIsOpen     = false;
uint32_t nextFrameMs   = 0;   // próximo instante permitido para avançar frame
uint8_t  currentBright = BRIGHTNESS_MAX;
uint32_t cycleCount    = 0;   // contador de ciclos completos

// ============================================================
// Helpers
// ============================================================

void setBacklight(uint8_t b) {
  analogWrite(TFT_BL, b);
  currentBright = b;
}

/** Interpolação linear de brilho baseada no tempo no estado GIF_PLAYING */
uint8_t calcBrightness(uint32_t elapsed) {
  if (elapsed >= DIM_DURATION_MS) return BRIGHTNESS_MIN;
  uint32_t range = BRIGHTNESS_MAX - BRIGHTNESS_MIN;
  uint8_t b = (uint8_t)(BRIGHTNESS_MAX - (range * elapsed) / DIM_DURATION_MS);
  return max((uint8_t)BRIGHTNESS_MIN, b);
}

void enterState(State s) {
  state        = s;
  stateEnterMs = millis();
}

/**
 * Envia uma linha de evento para o RPi 4 via USB Serial.
 * Formato: "EVENT:<nome>\n"  (ou com parâmetro: "EVENT:<nome>:<valor>\n")
 * O RPi lê esta porta e reage ao receber CAPTURE_READY.
 */
void sendEvent(const char *name, int32_t value = -1) {
  if (value >= 0) {
    Serial.printf("EVENT:%s:%ld\n", name, value);
  } else {
    Serial.printf("EVENT:%s\n", name);
  }
}

// ============================================================
// Callback de desenho – upscale nearest-neighbor para 240x240
// ============================================================
void GIFDraw(GIFDRAW *pDraw) {
  uint8_t  *s   = pDraw->pPixels;
  uint16_t *pal = pDraw->pPalette;

  int srcY = pDraw->iY + pDraw->y;
  int dstY0 = (srcY       * DISP_H) / GIF_H;
  int dstY1 = ((srcY + 1) * DISP_H) / GIF_H;

  bool    hasTransp     = (bool)pDraw->ucHasTransparency;
  uint8_t ucTransparent = pDraw->ucTransparent;

  static uint16_t scaledBuf[DISP_W];
  static bool     transBuf[DISP_W];

  for (int dstX = 0; dstX < DISP_W; dstX++) {
    int     srcX = (dstX * GIF_W) / DISP_W;
    uint8_t c    = s[srcX];
    if (hasTransp && c == ucTransparent) {
      transBuf[dstX]  = true;
      scaledBuf[dstX] = 0;
    } else {
      transBuf[dstX]  = false;
      scaledBuf[dstX] = pal[c];
    }
  }

  for (int dstY = dstY0; dstY < dstY1; dstY++) {
    if (hasTransp) {
      for (int x = 0; x < DISP_W;) {
        if (transBuf[x]) { x++; continue; }
        int start = x;
        while (x < DISP_W && !transBuf[x]) x++;
        tft.pushImage(start, dstY, x - start, 1, scaledBuf + start);
      }
    } else {
      tft.pushImage(0, dstY, DISP_W, 1, scaledBuf);
    }
  }
}

// ============================================================
// Setup
// ============================================================
void setup() {
  Serial.begin(115200);
  delay(500);
  Serial.println("[dimmer] RP2040 Zero – Iniciando...");

  // PWM do backlight (GP7) – 1 kHz, 8-bit
  pinMode(TFT_BL, OUTPUT);
  analogWriteFreq(1000);
  analogWriteRange(255);
  setBacklight(BRIGHTNESS_MAX);

  tft.init();
  tft.setRotation(0);

  // Pisca azul para confirmar display OK
  tft.fillScreen(TFT_BLUE);
  delay(400);
  tft.fillScreen(TFT_BLACK);

  // AnimatedGIF: ST7789 usa big-endian
  gif.begin(BIG_ENDIAN_PIXELS);

  // Abre o GIF uma vez aqui para validar
  if (!gif.open((uint8_t *)gatotft, sizeof(gatotft), GIFDraw)) {
    tft.fillScreen(TFT_RED);
    tft.setTextColor(TFT_WHITE, TFT_RED);
    tft.setTextSize(2);
    tft.drawString("ERRO GIF!", 50, 110);
    Serial.println("[dimmer] ERRO: nao foi possivel abrir o GIF!");
    while (true) delay(1000); // trava para diagnóstico
  }
  gifIsOpen    = true;
  nextFrameMs  = millis();
  enterState(GIF_PLAYING);

  Serial.printf("[dimmer] Config: dim=%lums | pausa=%lums | captura=%lums\n",
                DIM_DURATION_MS, PAUSE_DARK_MS, CAPTURE_HOLD_MS);
}

// ============================================================
// Loop principal – máquina de estados não-bloqueante
// ============================================================
void loop() {
  uint32_t now     = millis();
  uint32_t elapsed = now - stateEnterMs;

  switch (state) {

    // ── GIF rodando + dimming ──────────────────────────────
    case GIF_PLAYING: {
      // 1. Atualiza brilho (desacoplado do GIF)
      uint8_t target = calcBrightness(elapsed);
      if (target != currentBright) {
        setBacklight(target);
        Serial.printf("[dimmer] brilho=%3d t=%lums\n", target, elapsed);
      }

      // 2. Avança um frame do GIF quando for a hora
      //    playFrame(false, &delayMs) retorna o delay pedido pelo GIF
      //    sem bloquear – mantemos nosso próprio temporizador.
      if (now >= nextFrameMs && gifIsOpen) {
        int frameDelayMs = 0;
        bool more = gif.playFrame(false, &frameDelayMs);
        nextFrameMs = now + max(frameDelayMs, 1);

        if (!more) {
          // Fim do loop do GIF: fecha e reabre
          gif.close();
          gifIsOpen = false;
          if (gif.open((uint8_t *)gatotft, sizeof(gatotft), GIFDraw)) {
            gifIsOpen = true;
          }
        }
      }

      // 3. Brilho atingiu mínimo → pausa escura
      if (target <= BRIGHTNESS_MIN) {
        if (gifIsOpen) { gif.close(); gifIsOpen = false; }
        setBacklight(0);
        tft.fillScreen(TFT_BLACK);
        enterState(DARK_PAUSE);
        sendEvent("DARK_PAUSE");  // informa RPi: não capture agora
      }
      break;
    }

    // ── Tela escura aguardando ─────────────────────────────
    case DARK_PAUSE: {
      if (elapsed >= PAUSE_DARK_MS) {
        tft.fillScreen(TFT_WHITE);
        setBacklight(BRIGHTNESS_MAX);
        enterState(WHITE_CAPTURE);
        // ★ Evento principal: RPi deve capturar agora
        sendEvent("CAPTURE_READY", cycleCount);
      }
      break;
    }

    // ── Tela branca para captura ───────────────────────────
    case WHITE_CAPTURE: {
      if (elapsed >= CAPTURE_HOLD_MS) {
        cycleCount++;
        // Reinicia: reabre GIF e volta ao dimming
        setBacklight(BRIGHTNESS_MAX);
        tft.fillScreen(TFT_BLACK);
        if (gif.open((uint8_t *)gatotft, sizeof(gatotft), GIFDraw)) {
          gifIsOpen   = true;
          nextFrameMs = millis();
        }
        enterState(GIF_PLAYING);
        sendEvent("GIF_START", cycleCount);  // informa RPi: ciclo novo
      }
      break;
    }
  }
}
