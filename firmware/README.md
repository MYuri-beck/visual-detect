# Firmware — VisualDetect HID Controller

Este diretório contém os firmwares do controlador físico de botões do VisualDetect.
O controlador se conecta via **USB** ao Raspberry Pi 4 e se registra como **teclado HID padrão**,
permitindo que o operador navegue pela interface usando botões físicos.

---

## Firmware Ativo — Raspberry Pi Pico 2W

> ✅ **Este é o firmware em uso no hardware atual.**

| Campo | Valor |
|---|---|
| **Pasta** | `pico2w_hid_controller/` |
| **Arquivo** | `pico2w_hid_controller.ino` |
| **Hardware** | Raspberry Pi Pico 2W (RP2350) |
| **Ambiente** | Arduino IDE + core arduino-pico |
| **Biblioteca HID** | `Keyboard.h` (embutida no arduino-pico) |

### Documentação completa

Consulte [`pico2w_hid_controller/README.md`](pico2w_hid_controller/README.md) para:

- Esquema de pinos (GPIO → Tecla → Ação por tela)
- Instruções de instalação do core arduino-pico
- Como gravar o firmware (modo BOOTSEL)
- Lógica de debounce e debug serial
- Tabela comparativa ESP32 vs Pico 2W

---

## Firmware Legado — ESP32-S2/S3

> ⚠️ **Mantido como referência histórica. Não é o firmware em uso.**
> Substituído pelo firmware do Pico 2W em 31/08/2026.

| Campo | Valor |
|---|---|
| **Pasta** | `esp32_hid_controller/` |
| **Arquivo** | `esp32_hid_controller.ino` |
| **Hardware** | ESP32-S2 ou ESP32-S3 (USB nativo obrigatório) |
| **Ambiente** | Arduino IDE + core arduino-esp32 (Espressif) |
| **Biblioteca HID** | `USB.h` + `USBHIDKeyboard.h` (Espressif) |

> ⚠️ O firmware ESP32 usa bibliotecas (`USB.h`, `USBHIDKeyboard.h`) exclusivas do core
> Espressif e **não é compatível** com o Raspberry Pi Pico 2W.

---

## Mapeamento de Botões (ambos os firmwares)

O mapeamento de pinos e teclas é **idêntico** nos dois firmwares:

| Pino | Botão | Tecla HID | Ação principal no VisualDetect |
|---|---|---|---|
| GPIO 5 | Seta Direita | `RIGHT_ARROW` | Próximo item / avançar |
| GPIO 6 | Seta Esquerda | `LEFT_ARROW` | Item anterior / voltar |
| GPIO 7 | Seta Cima | `UP_ARROW` | Aumentar valor / item acima |
| GPIO 8 | Seta Baixo | `DOWN_ARROW` | Diminuir valor / item abaixo |
| GPIO 9 | Enter | `RETURN` | Confirmar / abrir |

Todos os pinos usam `INPUT_PULLUP` — conecte o botão entre GPIO e **GND**.

---

## Display TFT

A pasta `tft_display_154/` contém o firmware para o display TFT ST7789 (1.54").
Consulte a documentação interna dessa pasta para detalhes.

---

## Por que foi feita a troca ESP32 → Pico 2W?

- O Pico 2W possui USB HID nativo via RP2350 (ARM Cortex-M33), sem hardware adicional
- Maior disponibilidade no contexto do projeto (SENAI/NUDEP)
- Integração via Arduino IDE mantém o ambiente de desenvolvimento familiar
- O mapeamento de pinos e teclas é idêntico — **nenhuma alteração** foi necessária no app
- Consulte o caderno de campo `docs/caderno_campo_2026-08-31.md` para a decisão completa
