# Documentação Técnica — pico2w_hid_controller

## Visão Geral

| Campo | Valor |
|---|---|
| **Arquivo** | pico2w_hid_controller.ino |
| **Hardware alvo** | Raspberry Pi Pico 2W (RP2350) |
| **Função** | Emulador de teclado HID USB |
| **Destino** | Raspberry Pi 4 rodando VisualDetect (ui.py) |
| **Ambiente** | Arduino IDE + core arduino-pico (earlephilhower) |
| **Linguagem** | C++ (Arduino framework) |

---

## Descrição

O firmware transforma o Raspberry Pi Pico 2W em um **teclado USB HID**. Quando conectado ao Raspberry Pi 4 via cabo USB, o Pico é reconhecido pelo sistema operacional como um teclado padrão — sem drivers adicionais.

Cinco botões físicos são mapeados para as setas direcionais e Enter, que são exatamente as teclas capturadas pela interface gráfica do VisualDetect (ui.py) para navegação entre telas, ajuste de parâmetros e confirmação de ações.

---

## Hardware Necessário

| Componente | Quantidade | Observação |
|---|---|---|
| Raspberry Pi Pico 2W | 1 | Chip RP2350, com suporte USB nativo |
| Push-button (botão de pulso) | 5 | Normalmente aberto (NO) |
| Cabo USB-A → Micro-USB | 1 | Conecta Pico → Raspberry Pi 4 |

> **Nota:** O Pico 2W possui resistores de pull-up internos configuráveis via software — nenhum resistor externo é necessário.

---

## Esquema de Pinos

`
GPIO  | Função         | Tecla HID      | Ação no VisualDetect
------|----------------|----------------|-------------------------------
  5   | Botão Direita  | RIGHT_ARROW    | Próximo botão / próxima imagem
  6   | Botão Esquerda | LEFT_ARROW     | Botão anterior / voltar
  7   | Botão Cima     | UP_ARROW       | Aumentar valor / navegar acima
  8   | Botão Baixo    | DOWN_ARROW     | Diminuir valor / navegar abaixo
  9   | Botão Enter    | RETURN         | Confirmar / abrir
`

**Ligação física:** Conecte um lado do botão ao GPIO indicado e o outro ao **GND**.  
O pino é configurado como INPUT_PULLUP, portanto a lógica é **ativa em nível baixo** (LOW = pressionado).

---

## Mapeamento por Tela (VisualDetect)

| Tela | Left | Right | Up | Down | Enter |
|---|---|---|---|---|---|
| **T1 — Splash** | — | — | Seleciona INICIAR | Seleciona GALERIA | Confirma seleção |
| **T2 — Config** | Volta passo anterior | — | Aumenta valor | Diminui valor | Avança / confirma |
| **T3 — Revisão** | Seleciona VOLTAR | Seleciona INICIAR | — | — | Confirma seleção |
| **T4 — Capturando** | bloqueado | bloqueado | bloqueado | bloqueado | bloqueado |
| **T4b — Analisando** | bloqueado | bloqueado | bloqueado | bloqueado | bloqueado |
| **T5 — Concluído** | Seleciona NOVO EXAME | Seleciona GALERIA | — | — | Confirma seleção |
| **Galeria** | Volta nível anterior | — | Item acima | Item abaixo | Abre item selecionado |

---

## Dependências

### Arduino IDE — Board Manager

Adicionar a URL em Arquivo → Preferências → URLs adicionais para gerenciadores de placas:

`
https://github.com/earlephilhower/arduino-pico/releases/download/global/package_rp2040_index.json
`

Instalar em Ferramentas → Gerenciador de Placas → pesquisar por Raspberry Pi Pico/RP2040.

### Biblioteca Utilizada

| Biblioteca | Fonte | Função |
|---|---|---|
| Keyboard.h | Embutida no core arduino-pico | Emulação de teclado HID USB |

> **Atenção:** Esta biblioteca é diferente da USBHIDKeyboard.h usada no ESP32. São incompatíveis entre si.

---

## Configuração do Arduino IDE

1. Instalar o core rduino-pico via Board Manager (URL acima)
2. Selecionar placa: Ferramentas → Placa → Raspberry Pi Pico 2 W
3. Selecionar USB Stack: Ferramentas → USB Stack → TinyUSB
4. Selecionar porta COM correspondente ao Pico

---

## Como Gravar o Firmware

### Primeira gravação (modo BOOTSEL)

1. Segure o botão **BOOTSEL** no Pico
2. Conecte o cabo USB ao computador enquanto segura BOOTSEL
3. Solte o BOOTSEL — o Pico monta como pendrive (RPI-RP2)
4. No Arduino IDE, clique em **Upload** — o IDE transfere automaticamente

### Gravações subsequentes

Após a primeira gravação, o Arduino IDE consegue regravar via porta COM normalmente, sem precisar do modo BOOTSEL.

---

## Lógica do Firmware

### Inicialização (setup)

`
1. Inicia Serial (115200 baud) para debug
2. Configura GPIOs 5-9 como INPUT_PULLUP
3. Inicializa estado anterior de cada botão como HIGH (não pressionado)
4. Chama Keyboard.begin() — USB HID sobe automaticamente
`

### Loop principal (loop)

`
Para cada botão:
  1. Lê estado atual do GPIO (HIGH ou LOW)
  2. Detecta borda de descida: HIGH → LOW (pressão)
  3. Verifica debounce: tempo desde última detecção >= 30ms
  4. Se válido:
     a. Registra timestamp do debounce
     b. Imprime log na Serial
     c. Keyboard.press(tecla) → delay(15ms) → Keyboard.release(tecla)
  5. Atualiza estado anterior
Delay de 5ms ao final do loop
`

### Debounce

O debounce é implementado por **tempo** (millis()), não por flag de estado. Isso garante que:
- Pressões rápidas e legítimas não sejam ignoradas
- Ruído elétrico no momento do contato não gere teclas duplicadas
- O intervalo mínimo entre detecções é de **30ms**

---

## Debug Serial

Ao pressionar qualquer botão, o monitor serial (115200 baud) exibe:

`
=== Pico 2W HID Controller ===
Aguardando pressao de botoes...
[HID] Botao GPIO 5 -> Seta Direita (Right)
[HID] Botao GPIO 9 -> Enter        (Return)
`

---

## Diferenças em relação ao Firmware ESP32 Original

| Aspecto | ESP32-S2/S3 | Pico 2W |
|---|---|---|
| Biblioteca HID | USBHIDKeyboard.h | Keyboard.h |
| Inicialização USB | USB.begin() explícito | Automático |
| Core Arduino | rduino-esp32 (Espressif) | rduino-pico (earlephilhower) |
| Debounce | Por flag de estado | Por tempo (millis) — mais robusto |
| Chip | Xtensa LX7 / RISC-V | ARM Cortex-M33 (RP2350) |
| Pinos GPIO | Idênticos (5, 6, 7, 8, 9) | Idênticos (5, 6, 7, 8, 9) |
| Teclas mapeadas | Idênticas | Idênticas |

> A interface do VisualDetect (ui.py) não requer nenhuma alteração — o mapeamento de teclas é o mesmo.

---

## Integração com o VisualDetect

`
[ Botões físicos ]
        │
        │  GPIO INPUT_PULLUP
        ▼
[ Raspberry Pi Pico 2W ]
        │
        │  USB — Emulação HID Keyboard (TinyUSB)
        ▼
[ Raspberry Pi 4 — Sistema Operacional ]
        │
        │  Evento de teclado (KeyPress)
        ▼
[ app/main.py → app/ui.py ]
  handle_key(event) → ação na tela atual
`

O Pico 2W é completamente transparente para o sistema: o Raspberry Pi 4 o vê como um teclado USB genérico, sem necessidade de drivers, configurações de udev ou permissões especiais.
