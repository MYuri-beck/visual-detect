/**
 * @file    TFT_ST7789_test.ino
 * @brief   Código de teste para o display TFT 1.54" (240x240)
 * @project VisualDetect - Óculos de Estimulação Visual para Pacientes
 *
 * @hardware
 *   - Display: TFT 1.54 polegadas (240x240 pixels)
 *   - Controlador: ST7789
 *   - Biblioteca: TFT_eSPI (configurada via User_Setup.h)
 *
 * @description
 *   Teste básico de cores e texto para validação do hardware do display.
 *   Este sketch exibe uma sequência de cores (vermelho, verde, azul)
 *   com texto sobreposto para confirmar que os canais RGB estão funcionando.
 *
 * @note
 *   Antes de compilar, certifique-se que o arquivo User_Setup.h da biblioteca
 *   TFT_eSPI está configurado corretamente para o seu pinout.
 *
 * @todo
 *   - Desenvolver o código principal para exibição de estímulos visuais
 *   - Implementar comunicação com o ESP32 HID Controller (via BLE ou Serial)
 *   - Adicionar lógica de controle de frequência dos estímulos
 */

#include <SPI.h>
#include <TFT_eSPI.h> // Biblioteca principal que configuramos

TFT_eSPI tft = TFT_eSPI(); // Inicializa o objeto do display

void setup() {
  // Inicializa o hardware do display e aplica as configurações do User_Setup
  tft.init();

  // Define a rotação da tela: 0, 1, 2 ou 3 (ajuste se o texto ficar de ponta-cabeça)
  tft.setRotation(1);

  // Limpa a tela preenchendo com a cor preta
  tft.fillScreen(TFT_BLACK);

  // Configura a cor do texto (Texto Branco com fundo Preto)
  tft.setTextColor(TFT_WHITE, TFT_BLACK);

  // Define o tamanho do texto (1 é o padrão, 2 ou 3 fica maior e mais fácil de ler)
  tft.setTextSize(2);

  // Mensagem inicial de confirmação do sistema
  // Tela 240x240: posição (30, 110) aproxima o texto do centro vertical
  tft.drawString("SISTEMA OK!", 30, 110);

  // Aguarda 3 segundos exibindo a mensagem inicial antes de começar o pisca-pisca
  delay(3000);
}

void loop() {
  // --- Teste do canal Vermelho ---
  tft.fillScreen(TFT_RED);
  tft.setTextColor(TFT_WHITE, TFT_RED);
  tft.drawString("TELA VERMELHA", 30, 110);
  delay(1500);

  // --- Teste do canal Verde ---
  tft.fillScreen(TFT_GREEN);
  tft.setTextColor(TFT_BLACK, TFT_GREEN); // Texto preto para dar contraste no verde
  tft.drawString("TELA VERDE", 45, 110);
  delay(1500);

  // --- Teste do canal Azul ---
  tft.fillScreen(TFT_BLUE);
  tft.setTextColor(TFT_WHITE, TFT_BLUE);
  tft.drawString("TELA AZUL", 55, 110);
  delay(1500);
}
