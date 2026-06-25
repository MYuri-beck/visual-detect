/**
 * @file    TFT_ST7789_draw.ino
 * @brief   Reprodutor de GIF animado no display TFT 1.54" (240x240, ST7789)
 *          GIF atual: Gato animado (25 frames, 103x103)
 *          Upscale nearest-neighbor para preencher 240x240.
 *
 * @project VisualDetect - Oculos de Estimulacao Visual
 *
 * @hardware
 *   - MCU    : ESP32
 *   - Display: TFT 1.54" ST7789  (240 x 240)
 *
 * @pinout  (conforme User_Setup.h do projeto)
 *   MOSI -> GPIO 23 | SCLK -> GPIO 18
 *   CS   -> GPIO 19 | DC   -> GPIO  2
 *   RST  -> GPIO  4 | BL   -> GPIO 22
 *
 * @dependencies
 *   - TFT_eSPI    (Bodmer)      -- Gerenciador de Bibliotecas
 *   - AnimatedGIF (Larry Bank)  -- Gerenciador de Bibliotecas
 *   - gatotft.h                 -- mesma pasta do .ino
 */

#include <Arduino.h>
#include <SPI.h>
#include <TFT_eSPI.h>
#include <AnimatedGIF.h>
#include "gatotft.h"

// ============================================================
// Objetos globais
// ============================================================
TFT_eSPI    tft;
AnimatedGIF gif;

// ============================================================
// Dimensoes do GIF de origem e do display de destino
// ============================================================
#define GIF_W   103
#define GIF_H   103
#define DISP_W  240
#define DISP_H  240

// ============================================================
// Callback de desenho com upscale nearest-neighbor
//
// Cada pixel de origem (srcX, srcY) e mapeado para a faixa de
// pixels de destino correspondente, preenchendo o display inteiro.
//
// Transparencia: segmentos transparentes sao pulados, preservando
// o frame anterior naquelas posicoes (ghosting correto).
// ============================================================
void GIFDraw(GIFDRAW *pDraw) {
  uint8_t  *s   = pDraw->pPixels;
  uint16_t *pal = pDraw->pPalette;

  // Linha de origem (0..GIF_H-1)
  int srcY = pDraw->iY + pDraw->y;

  // Faixa de linhas de destino para esta linha de origem
  int dstY0 = (srcY       * DISP_H) / GIF_H;
  int dstY1 = ((srcY + 1) * DISP_H) / GIF_H;  // exclusivo

  bool    hasTransp    = (bool)pDraw->ucHasTransparency;
  uint8_t ucTransparent = pDraw->ucTransparent;

  // Buffers estaticos para nao usar a pilha (IRAM)
  static uint16_t scaledBuf[DISP_W];
  static bool     transBuf[DISP_W];

  // --- Passo 1: montar a linha escalada em X (nearest-neighbor) ---
  for (int dstX = 0; dstX < DISP_W; dstX++) {
    int     srcX = (dstX * GIF_W) / DISP_W;
    uint8_t c    = s[srcX];

    if (hasTransp && c == ucTransparent) {
      transBuf[dstX] = true;
      scaledBuf[dstX] = 0;
    } else {
      transBuf[dstX]  = false;
      scaledBuf[dstX] = pal[c];
    }
  }

  // --- Passo 2: enviar a linha para cada dstY mapeado ---
  for (int dstY = dstY0; dstY < dstY1; dstY++) {

    if (hasTransp) {
      // Envia apenas segmentos opacos contiguos
      int x = 0;
      while (x < DISP_W) {
        if (transBuf[x]) { x++; continue; }
        int start = x;
        while (x < DISP_W && !transBuf[x]) x++;
        tft.pushImage(start, dstY, x - start, 1, scaledBuf + start);
      }
    } else {
      // Linha totalmente opaca: envia de uma vez
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
  Serial.println("[gif_gato] Iniciando...");

  tft.init();
  tft.setRotation(1);

  // Backlight
  pinMode(TFT_BL, OUTPUT);
  digitalWrite(TFT_BL, TFT_BACKLIGHT_ON);

  // Teste visual: pisca verde para confirmar display OK
  tft.fillScreen(TFT_GREEN);
  delay(600);
  tft.fillScreen(TFT_BLACK);

  gif.begin(BIG_ENDIAN_PIXELS);  // ST7789 usa big-endian

  Serial.println("[gif_gato] Pronto! Iniciando loop do GIF...");
}

// ============================================================
// Loop: abre o GIF da flash e reproduz em loop infinito
// ============================================================
void loop() {
  if (gif.open((uint8_t *)gatotft,
               sizeof(gatotft),
               GIFDraw)) {

    Serial.printf("[gif_gato] GIF aberto: %d x %d\n",
                  gif.getCanvasWidth(),
                  gif.getCanvasHeight());

    while (gif.playFrame(true, NULL)) {
      // true = respeita o delay de cada frame automaticamente
    }

    gif.close();

  } else {
    Serial.println("[gif_gato] ERRO ao abrir o GIF!");
    tft.fillScreen(TFT_RED);
    tft.setTextColor(TFT_WHITE, TFT_RED);
    tft.setTextSize(2);
    tft.drawString("ERRO GIF!", 50, 110);
    delay(2000);
  }
}
