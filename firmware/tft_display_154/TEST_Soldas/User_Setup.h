// ============================================================
//  User_Setup.h  –  TFT_eSPI para RP2040 Zero + ST7789 240x240
//  Projeto: VisualDetect – Óculos de Estimulação Visual
// ============================================================

#define USER_SETUP_INFO "RP2040-Zero ST7789 240x240"

// ---------- Driver ------------------------------------------
#define ST7789_DRIVER

// ---------- Resolução ----------------------------------------
#define TFT_WIDTH  240
#define TFT_HEIGHT 240

// ---------- Pinos SPI (SPI0 – hardware) ----------------------
//  Display   RP2040 Zero
//  GND    →  GND
//  VCC    →  3.3V
//  SCL    →  GP2  (SPI0 SCK)
//  SDA    →  GP3  (SPI0 MOSI)
//  RES    →  GP4  (RST)
//  DC     →  GP5
//  CS     →  GP6
//  BL     →  GP7  (PWM – controle de brilho)
#define TFT_MOSI   3
#define TFT_SCLK   2
#define TFT_CS     6
#define TFT_DC     5
#define TFT_RST    4
#define TFT_BL     7
#define TFT_BACKLIGHT_ON HIGH

// ---------- Velocidade SPI -----------------------------------
// ST7789 suporta até ~62 MHz; 40 MHz é seguro para fios curtos
#define SPI_FREQUENCY       40000000
#define SPI_READ_FREQUENCY   6000000

// ---------- Fontes (opcional) --------------------------------
#define LOAD_GLCD
#define LOAD_FONT2
#define LOAD_FONT4

// ---------- Outras opções ------------------------------------
#define SUPPORT_TRANSACTIONS
