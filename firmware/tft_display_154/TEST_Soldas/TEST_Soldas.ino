/**
 * @file    TEST_Soldas.ino
 * @brief   Teste de soldagem – RP2040 Zero + ST7789 240x240
 *
 * Sequência:
 *   1. GIF animado por 10 segundos (brilho máximo)
 *   2. Escurece gradualmente em 5 segundos
 *   3. Tela preta por 1 segundo
 *   4. Tela BRANCA com brilho máximo por 3 segundos
 *   5. Volta para o passo 1 (loop infinito)
 *
 * Se cada etapa funcionar corretamente, as soldas estão OK.
 *
 * @pinout
 *   Display  →  RP2040 Zero
 *   GND      →  GND
 *   VCC      →  3.3V
 *   SCL      →  GP2
 *   SDA      →  GP3
 *   RES      →  GP4
 *   DC       →  GP5
 *   CS       →  GP6
 *   BL       →  GP7
 *
 * @dependencies
 *   - TFT_eSPI    (Bodmer)
 *   - AnimatedGIF (Larry Bank)
 *   Copie o User_Setup.h desta pasta para dentro de libraries/TFT_eSPI/
 */

#include <Arduino.h>
#include <SPI.h>
#include <TFT_eSPI.h>
#include <AnimatedGIF.h>
#include "gatotft.h"

// ── Tempos (ms) ──────────────────────────────────────────────
#define GIF_DURATION_MS    10000   // quanto tempo o GIF roda antes de escurecer
#define DIM_DURATION_MS     5000   // duração do escurecimento
#define DARK_PAUSE_MS       1000   // tela preta antes do branco
#define WHITE_DURATION_MS   3000   // duração da tela branca

// ── Display ───────────────────────────────────────────────────
#define DISP_W  240
#define DISP_H  240
#define GIF_W   103
#define GIF_H   103

TFT_eSPI    tft;
AnimatedGIF gif;

// ── Backlight ─────────────────────────────────────────────────
void setBL(uint8_t brightness) {
  analogWrite(TFT_BL, brightness);
}

// ── Callback do GIF (upscale nearest-neighbor) ────────────────
void GIFDraw(GIFDRAW *pDraw) {
  uint8_t  *s   = pDraw->pPixels;
  uint16_t *pal = pDraw->pPalette;

  int srcY = pDraw->iY + pDraw->y;
  int dstY0 = (srcY       * DISP_H) / GIF_H;
  int dstY1 = ((srcY + 1) * DISP_H) / GIF_H;

  bool    hasT = (bool)pDraw->ucHasTransparency;
  uint8_t ucT  = pDraw->ucTransparent;

  static uint16_t buf[DISP_W];
  static bool     trn[DISP_W];

  for (int x = 0; x < DISP_W; x++) {
    uint8_t c = s[(x * GIF_W) / DISP_W];
    trn[x] = hasT && c == ucT;
    buf[x] = trn[x] ? 0 : pal[c];
  }

  for (int dstY = dstY0; dstY < dstY1; dstY++) {
    if (hasT) {
      for (int x = 0; x < DISP_W;) {
        if (trn[x]) { x++; continue; }
        int s = x;
        while (x < DISP_W && !trn[x]) x++;
        tft.pushImage(s, dstY, x - s, 1, buf + s);
      }
    } else {
      tft.pushImage(0, dstY, DISP_W, 1, buf);
    }
  }
}

// ── Roda o GIF por 'duration' ms ─────────────────────────────
void playGIF(uint32_t duration) {
  bool open = gif.open((uint8_t *)gatotft, sizeof(gatotft), GIFDraw);
  if (!open) {
    tft.fillScreen(TFT_RED);
    tft.setTextColor(TFT_WHITE, TFT_RED);
    tft.setTextSize(2);
    tft.drawString("ERRO GIF!", 50, 110);
    delay(3000);
    return;
  }

  uint32_t start     = millis();
  uint32_t nextFrame = millis();

  while (millis() - start < duration) {
    if (millis() >= nextFrame) {
      int frameMs = 0;
      if (!gif.playFrame(false, &frameMs)) {
        // fim do loop: reabre
        gif.close();
        gif.open((uint8_t *)gatotft, sizeof(gatotft), GIFDraw);
        nextFrame = millis();
      } else {
        nextFrame = millis() + max(frameMs, 1);
      }
    }
  }

  gif.close();
}

// ── Escurece gradualmente de MAX até 0 em 'duration' ms ──────
void dimDown(uint32_t duration) {
  uint32_t start = millis();
  uint32_t nextFrame = millis();
  bool gifOpen = gif.open((uint8_t *)gatotft, sizeof(gatotft), GIFDraw);

  while (true) {
    uint32_t elapsed = millis() - start;
    if (elapsed >= duration) break;

    // Brilho linear: 255 → 0
    uint8_t bright = (uint8_t)(255UL * (duration - elapsed) / duration);
    setBL(bright);

    // Continua rodando o GIF durante o escurecimento
    if (gifOpen && millis() >= nextFrame) {
      int frameMs = 0;
      if (!gif.playFrame(false, &frameMs)) {
        gif.close();
        gif.open((uint8_t *)gatotft, sizeof(gatotft), GIFDraw);
        nextFrame = millis();
      } else {
        nextFrame = millis() + max(frameMs, 1);
      }
    }
  }

  if (gifOpen) gif.close();
  setBL(0);
}

// ── Setup ─────────────────────────────────────────────────────
void setup() {
  Serial.begin(115200);

  pinMode(TFT_BL, OUTPUT);
  analogWriteFreq(1000);   // 1 kHz PWM
  analogWriteRange(255);
  setBL(255);

  tft.init();
  tft.setRotation(0);

  gif.begin(BIG_ENDIAN_PIXELS);

  // ── Teste de display: pisca 3 cores ──
  Serial.println("[teste] Verificando display...");
  tft.fillScreen(TFT_RED);   delay(400);
  tft.fillScreen(TFT_GREEN); delay(400);
  tft.fillScreen(TFT_BLUE);  delay(400);
  tft.fillScreen(TFT_BLACK);

  Serial.println("[teste] Display OK! Iniciando sequência de teste...");
}

// ── Loop ──────────────────────────────────────────────────────
void loop() {
  // 1. GIF com brilho máximo
  Serial.println("[teste] GIF rodando...");
  setBL(255);
  playGIF(GIF_DURATION_MS);

  // 2. Escurece gradualmente mantendo o GIF
  Serial.println("[teste] Escurecendo...");
  dimDown(DIM_DURATION_MS);

  // 3. Tela preta – pausa
  Serial.println("[teste] Tela preta.");
  tft.fillScreen(TFT_BLACK);
  setBL(0);
  delay(DARK_PAUSE_MS);

  // 4. Tela BRANCA com brilho máximo
  Serial.println("[teste] TELA BRANCA (captura).");
  tft.fillScreen(TFT_WHITE);
  setBL(255);
  delay(WHITE_DURATION_MS);

  // 5. Volta ao inicio (loop automatico)
  Serial.println("[teste] Reiniciando ciclo.\n");
}
