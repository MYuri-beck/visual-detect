# Firmware — ESP32 HID Controller

Firmware para **ESP32-S2/S3** (com USB nativo) que emula um teclado HID via USB.
Permite controlar a interface do `batch_processor.py` no Raspberry Pi 4 através de botões físicos.

---

## Hardware necessário

| Componente | Detalhe |
|---|---|
| ESP32-S2 ou ESP32-S3 | Obrigatório — possui USB nativo (CDC + HID) |
| 5× botões de pulso (push-button) | Um por função |
| Cabo USB-C / Micro-USB | Conecta ESP32 → Raspberry Pi 4 |

> ⚠️ **ESP32 clássico (sem USB nativo) não suporta as bibliotecas `USB.h` / `USBHIDKeyboard.h`.**  
> Use apenas ESP32-S2 ou ESP32-S3.

---

## Esquema de pinos

```
Pino 5  → Seta Direita  (Next)
Pino 6  → Seta Esquerda (Back)
Pino 7  → Seta Cima     (Mais / +)
Pino 8  → Seta Baixo    (Menos / -)
Pino 9  → Enter         (Confirmar / Capturar)
```

Todos os pinos usam `INPUT_PULLUP`. Conecte um lado do botão ao pino e o outro ao **GND**.

---

## Dependências (Arduino IDE)

| Biblioteca | Fonte |
|---|---|
| `USB.h` | Embutida no pacote ESP32 Arduino (Espressif) |
| `USBHIDKeyboard.h` | Embutida no pacote ESP32 Arduino (Espressif) |

**Board Manager URL:**
```
https://raw.githubusercontent.com/espressif/arduino-esp32/gh-pages/package_esp32_index.json
```

**Board selecionada:** `ESP32S2 Dev Module` ou `ESP32S3 Dev Module`

---

## Como gravar o firmware

1. Instale o suporte ESP32 no Arduino IDE via Board Manager.
2. Selecione a placa correta (`Tools → Board → ESP32S2 Dev Module`).
3. Conecte o ESP32 em modo de boot (segure BOOT, pressione RESET, solte BOOT).
4. Abra `esp32_hid_controller.ino` e clique em **Upload**.
5. Após gravação, reconecte normalmente no Raspberry Pi 4.

---

## Integração com o batch_processor.py

O ESP32 se registra no Raspberry Pi 4 como um **teclado USB padrão** (HID).  
O `batch_processor.py` pode capturar os eventos de teclado normalmente (ex.: com `curses`, `keyboard`, ou `pynput`).

```
ESP32 (botões físicos)
    │
    │  USB HID Keyboard
    ▼
Raspberry Pi 4
    │
    ▼
batch_processor.py  (captura eventos de teclado)
```
