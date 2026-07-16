# TFT Display 1.54" — Firmware

Pasta dedicada ao firmware do **display TFT 1.54 polegadas** (240×240 px) utilizado no protótipo dos óculos do projeto **VisualDetect**.

---

## 📁 Estrutura

```
tft_display_154/
├── tft_display_154.ino      # Sketch de teste de cores e validação do hardware
├── README.md                # Este arquivo
└── lib_config/
    ├── User_Setup.h         # Configuração principal da lib TFT_eSPI
    └── User_Setup_Select.h  # Seleciona o Setup24_ST7789.h (ativo)
```

---

## 🔧 Hardware

| Componente | Detalhe |
|---|---|
| **Display** | TFT 1.54" — 240 × 240 pixels |
| **Controlador** | **ST7789** |
| **Interface** | SPI |
| **Microcontrolador** | ESP8266 NodeMCU |
| **Biblioteca** | [TFT_eSPI (Bodmer)](https://github.com/Bodmer/TFT_eSPI) |

---

## ⚙️ Configuração da Biblioteca TFT_eSPI

> [!IMPORTANT]
> Os arquivos dentro de `lib_config/` devem ser **copiados** para dentro da pasta da biblioteca TFT_eSPI instalada, substituindo os originais.
>
> Caminho padrão no Windows:
> ```
> C:\Users\<seu_usuario>\Documents\Arduino\libraries\TFT_eSPI\
> ```

### Como instalar

1. Instale a biblioteca **TFT_eSPI** pelo Library Manager da Arduino IDE
2. Copie `lib_config/User_Setup.h` → substitua o `User_Setup.h` na pasta da lib
3. Copie `lib_config/User_Setup_Select.h` → substitua o `User_Setup_Select.h` na pasta da lib
4. Recompile o sketch

---

## 📌 Setup Ativo: `Setup24_ST7789.h`

O arquivo `User_Setup_Select.h` está configurado para usar o **Setup24** — preset oficial da TFT_eSPI para o display ST7789 240×240 com ESP8266/ESP32.

```cpp
// Linha ativa no User_Setup_Select.h:
#include <User_Setups/Setup24_ST7789.h>  // ST7789 240 x 240
```

### Pinout — ESP8266 NodeMCU

| Sinal TFT | Pino NodeMCU | GPIO |
|---|---|---|
| **MISO** | D6 | GPIO12 |
| **MOSI** | D7 | GPIO13 |
| **SCLK** | D5 | GPIO14 |
| **CS** | D8 | GPIO15 |
| **DC** | D3 | GPIO0 |
| **RST** | D4 | GPIO2 |
| **VCC** | 3.3V | — |
| **GND** | GND | — |

> [!NOTE]
> O `User_Setup.h` atualmente tem os pinos configurados para **ESP8266 NodeMCU**.
> Se for usar com ESP32, descomente a seção ESP32 e comente a seção ESP8266 no arquivo.

### Velocidade SPI configurada

```cpp
#define SPI_FREQUENCY      27000000  // 27 MHz (escrita)
#define SPI_READ_FREQUENCY 20000000  // 20 MHz (leitura)
```

### Fontes carregadas

| Define | Fonte |
|---|---|
| `LOAD_GLCD` | Font 1 — Adafruit 8px |
| `LOAD_FONT2` | Font 2 — 16px |
| `LOAD_FONT4` | Font 4 — 26px |
| `LOAD_FONT6` | Font 6 — 48px (números) |
| `LOAD_FONT7` | Font 7 — 7 segmentos 48px |
| `LOAD_FONT8` | Font 8 — 75px (números) |
| `LOAD_GFXFF` | FreeFonts — 48 fontes Adafruit GFX |
| `SMOOTH_FONT` | Fonte suave com SPIFFS |

---

## 🧪 O que o Sketch de Teste faz

1. **Inicializa** o display e exibe `"SISTEMA OK!"` por 3 segundos
2. **Cicla** entre as cores primárias com texto sobreposto:
   - 🔴 Vermelho → `"TELA VERMELHA"`
   - 🟢 Verde → `"TELA VERDE"`
   - 🔵 Azul → `"TELA AZUL"`

O teste confirma que os **três canais RGB** do display estão funcionando corretamente.

---

## 🗺️ Próximos Passos

- [ ] Desenvolver o firmware principal dos óculos de estimulação visual
- [ ] Implementar exibição de padrões/estímulos visuais para o paciente
- [ ] Integrar comunicação com o `esp32_hid_controller` (BLE / Serial)
- [ ] Adicionar controle de frequência e intensidade dos estímulos
- [ ] Adaptar pinout para ESP32 se necessário

---

## 📂 Estrutura do Projeto

```
firmware/
├── esp32_hid_controller/   # Controlador HID via ESP32
│   └── esp32_hid_controller.ino
└── tft_display_154/        # ← Você está aqui
    ├── README.md
    ├── tft_display_154.ino
    └── lib_config/
        ├── User_Setup.h
        └── User_Setup_Select.h
```
