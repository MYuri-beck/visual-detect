# Manual Técnico — VisualDetect

> **Projeto:** VisualDetect — Equipamento de Triagem do Reflexo Ocular
> **Versão:** 1.2 · Outubro 2026
> **Autores:** Yuri Mendes
> **Instituição:** SENAI / NUDEP

---

## Índice

1. [Visão Geral do Sistema](#1-visão-geral-do-sistema)
2. [Arquitetura Geral](#2-arquitetura-geral)
3. [Estrutura de Arquivos](#3-estrutura-de-arquivos)
4. [Módulo `main.py`](#4-módulo-mainpy--ponto-de-entrada)
5. [Módulo `backend.py`](#5-módulo-backendpy--camada-de-lógica)
6. [Módulo `ui.py`](#6-módulo-uipy--interface-gráfica)
7. [Fluxo Completo de um Exame](#7-fluxo-completo-de-um-exame)
8. [Comunicação entre Threads](#8-comunicação-entre-threads)
9. [Sistema de Arquivos Gerados](#9-sistema-de-arquivos-gerados)
10. [Firmware — pico2w_hid_controller](#10-firmware--pico2w_hid_controller)
11. [Integração Hardware-Software](#11-integração-hardware-software)
12. [Dependências e Requisitos](#12-dependências-e-requisitos)
13. [Configurações e Parâmetros Ajustáveis](#13-configurações-e-parâmetros-ajustáveis)
14. [Navegação por Teclado / HID](#14-navegação-por-teclado--hid)
15. [Modo Touchscreen (TOUCH_MODE)](#15-modo-touchscreen-touch_mode)

---

## 1. Visão Geral do Sistema

O **VisualDetect** é um sistema embarcado de triagem do reflexo ocular desenvolvido para auxiliar na detecção precoce do Retinoblastoma. O sistema combina:

- **Software Python** rodando em Raspberry Pi 4 (ou PC para desenvolvimento)
- **Firmware Arduino** no Raspberry Pi Pico 2W, que emula um teclado HID USB para controle físico via botões
- **Modelo YOLO** treinado para detecção de anomalias oculares via visão computacional

O equipamento suporta **dois modos de operação** configuráveis via código:

| Modo | Constante | Descrição |
|------|-----------|-----------|
| **Touchscreen** | `TOUCH_MODE = True` | Navegação por toque/clique (padrão atual) |
| **HID / Teclado** | `TOUCH_MODE = False` | Navegação exclusiva via 5 botões físicos (Pico 2W) |

### Stack tecnológico

| Camada | Tecnologia | Versão mínima |
|--------|------------|---------------|
| Linguagem | Python | 3.11 |
| Interface gráfica | CustomTkinter (`ctk`) | 5.x (PC) / 6.0.0 (RPi) |
| Visão computacional | Ultralytics YOLO | 8.x |
| Captura de imagem | OpenCV (`cv2`) | 4.x (PC) / 5.0.0 (RPi) |
| Exibição de imagens | Pillow (PIL) | 9.x (PC) / 12.x (RPi) |
| Firmware controller | Arduino + arduino-pico | RP2350 |

---

## 2. Arquitetura Geral

O sistema segue uma arquitetura em três camadas com **injeção de dependência** — a UI nunca instancia backends diretamente.

```mermaid
graph TD
    A["main.py\n(ponto de entrada)"] --> B["CameraManager\n(thread câmera ~30 FPS)"]
    A --> C["VisionAnalyzer\n(carregamento YOLO async)"]
    A --> D["CaptureSession\n(coordena exame)"]
    B --> D
    C --> D
    D --> E["VisualDetectUI\n(ui.py — CustomTkinter)"]

    style A fill:#1a1533,color:#fff,stroke:#7c4dff
    style B fill:#1a1533,color:#00e676,stroke:#00e676
    style C fill:#1a1533,color:#00e676,stroke:#00e676
    style D fill:#252040,color:#fff,stroke:#7c4dff
    style E fill:#252040,color:#fff,stroke:#7c4dff
```

**Princípios de design:**

| Princípio | Implementação |
|-----------|---------------|
| Separação de responsabilidades | `backend.py` não importa nada de `ui.py` e vice-versa |
| Injeção de dependência | `CaptureSession` é criada em `main.py` e entregue à UI |
| Thread safety | Toda atualização de widget vinda de thread usa `after(0, callback)` |
| Graceful degradation | `cv2` e `ultralytics` são opcionais — o app inicializa mesmo sem eles |

---

## 3. Estrutura de Arquivos

```
app/
├── main.py                              # Ponto de entrada — configura e conecta as camadas
├── backend.py                           # Lógica: câmera, YOLO, sessão de exame
├── ui.py                                # Interface gráfica (todas as telas)
│
├── assets/                              # Recursos visuais (logos PNG)
│   ├── logo - VisualDetect_greenPupil_png-Photoroom.png
│   ├── logo - VisualDetect.png
│   ├── logo - NUDEP_branco_png.png
│   └── logo - NUDEP_png.png
│
├── models/
│   └── best.pt                          # Modelo YOLO treinado (não incluso no repo)
│
├── capturas_voluntarios_analisar/       # Imagens brutas capturadas durante exames
│   └── YYYYMMDD_HHMMSS_capture_N.jpg
│
└── capturas_analisadas_voluntarios/     # Imagens com anotações YOLO por exame
    └── Exame DD-MM-YY - HH-MM/
        ├── Analise 01.jpg
        ├── Analise 02.jpg
        └── detections.json

firmware/
├── README.md
├── pico2w_hid_controller/               # Firmware ATIVO
│   ├── pico2w_hid_controller.ino        # Pico 2W → HID USB (RP2350)
│   └── README.md
└── esp32_hid_controller/               # Legado — ESP32-S2/S3 (não utilizado)
    └── esp32_hid_controller.ino

docs/
├── dev/
│   ├── MANUAL_TECNICO.md               # Este arquivo
│   ├── INSTALL_RASPBERRY.md            # Guia de instalação no Raspberry Pi
│   ├── INSTALL_PC.md                   # Guia para desenvolvimento no Windows
│   ├── install_rpi.sh                  # Script de instalação automática (RPi)
│   ├── visualdetect.service            # Serviço systemd para autostart
│   └── CADERNO_CAMPO_*.md              # Diários de campo das sessões
└── user_guide/
    └── GUIA_DO_USUARIO.md              # Guia do operador / médico

# Pastas de desenvolvimento (não fazem parte do deploy no Raspberry Pi)
training/                               # Scripts e configs de treinamento YOLO
data/                                   # Datasets e anotações
analysis/                               # Análises exploratórias e notebooks
scripts/                                # Utilitários auxiliares
runs/                                   # Resultados de treinamento YOLO (auto-gerado)
capture/                                # Capturas avulsas de desenvolvimento

requirements_pc.txt                     # Dependências Python para desenvolvimento (PC)
requirements_rpi.txt                    # Dependências Python fixas para Raspberry Pi
```

---

## 4. Módulo `main.py` — Ponto de Entrada

**Linhas:** 95 | **Responsabilidade:** configuração, composição, inicialização.

> Para o guia completo de instalação e deploy no Raspberry Pi, consulte [`docs/dev/INSTALL_RASPBERRY.md`](INSTALL_RASPBERRY.md).

### Parâmetros configuráveis

```python
MODELO_PATH     = os.path.join(_APP_DIR, "models", "best.pt")
CAPTURE_FOLDER  = os.path.join(_APP_DIR, "capturas_voluntarios_analisar")
ANALYZED_FOLDER = os.path.join(_APP_DIR, "capturas_analisadas_voluntarios")
```

> Para alterar qualquer caminho, edite apenas as três constantes acima.

### Sequência de inicialização

```mermaid
sequenceDiagram
    participant M as main.py
    participant Cam as CameraManager
    participant Ana as VisionAnalyzer
    participant Ses as CaptureSession
    participant UI as VisualDetectUI

    M->>Cam: CameraManager()
    M->>Cam: camera.start() — thread inicia (index=0)
    M->>Ana: VisionAnalyzer(model_path)
    M->>Ses: CaptureSession(camera, analyzer, ...)
    M->>UI: VisualDetectUI(backend_session=session)
    UI->>Ana: load_async() — YOLO carrega em background
    M->>UI: app.mainloop() — bloqueia aqui
    Note over M,UI: Ao fechar a janela
    M->>Cam: camera.stop()
```

### Como executar

```bash
python main.py              # janela 800×480 (desenvolvimento)
python main.py --fullscreen # tela cheia (Raspberry Pi em produção)
python main.py -f           # equivalente ao acima
```

### Atalhos de teclado globais (VisualDetectUI)

| Tecla | Ação |
|-------|------|
| `F11` | Alterna fullscreen / janela |
| `ESC` | Sai do fullscreen; ou fecha a aplicação |

---

## 5. Módulo `backend.py` — Camada de Lógica

**Linhas:** 419 | Dependências externas com **graceful degradation**:

```python
CV2_AVAILABLE  = True   # False se opencv não instalado → câmera desabilitada
YOLO_AVAILABLE = True   # False se ultralytics não instalado → análise desabilitada
```

---

### 5.1 CameraManager

Gerencia a webcam em **thread separada** para não bloquear a UI.

#### Métodos públicos

| Método | Retorno | Descrição |
|--------|---------|-----------|
| `start(index=0)` | `bool` | Abre câmera e inicia thread. `0` = webcam padrão (USB ou integrada) |
| `stop()` | — | Para a thread e libera o hardware |
| `get_frame()` | `ndarray \| None` | Retorna cópia do frame BGR mais recente (thread-safe) |
| `available` | `bool` | `True` se câmera está aberta e operacional |

> **Nota v1.1:** O índice padrão foi alterado de `1` para `0`. Para câmera USB secundária, passe `index=1` explicitamente.

#### Detalhes internos

- Frame espelhado horizontalmente com `cv2.flip(frame, 1)` — comportamento natural de espelho
- Buffer interno protegido por `threading.Lock()`
- Sempre retorna uma **cópia** do frame (nunca referência direta)
- Frequência de captura: ~30 FPS (`time.sleep(0.033)`)
- **Parada automática na T4b** para liberar CPU do Raspberry Pi durante análise YOLO

```mermaid
graph LR
    A["Thread UI"] -- "get_frame()" --> L{Lock}
    L -- "retorna cópia de _frame" --> A
    B["Thread Câmera\n(_loop)"] -- "cap.read() + flip → _frame" --> L
    B -- "sleep 0.033s" --> B
```

---

### 5.2 VisionAnalyzer

Carrega e executa o modelo YOLO para detecção de anomalias oculares.

#### Métodos públicos

| Método | Descrição |
|--------|-----------|
| `load_sync()` | Carrega o modelo bloqueando a thread chamadora |
| `load_async(on_ready=None)` | Carrega em background; chama `on_ready()` ao concluir |
| `analyze_file(image_path, output_path)` | Analisa imagem, salva resultado com bounding boxes, retorna detecções |
| `available` | `True` se modelo foi carregado com sucesso |
| `is_loading` | `True` enquanto carregamento está em andamento |

#### Retorno de `analyze_file`

```python
# Lista de tuplas (label, confiança)
[("normal", 0.9321), ("anomalia", 0.7854)]

# Lista vazia se modelo indisponível ou erro
[]
```

#### Fluxo de carregamento assíncrono

```mermaid
sequenceDiagram
    participant SL as ScreenLoading (UI)
    participant VA as VisionAnalyzer
    participant W as Thread Worker

    SL->>VA: load_async(on_ready=callback)
    VA->>W: threading.Thread(target=_load).start()
    Note over SL: UI continua animando (barra indeterminada)
    W->>W: YOLO(model_path) — pode demorar 10-30s
    W->>SL: after(0, callback)
    SL->>SL: Exibe "Pronto!" por 600ms
    SL->>SL: show_screen("t0")
```

---

### 5.3 CaptureSession

Coordena o fluxo completo de um exame: captura periódica, análise YOLO e dados para a galeria.

#### Parâmetros de exame (ajustados pela tela T2)

| Atributo | Padrão | Range | Descrição |
|----------|--------|-------|-----------|
| `image_number` | 10 | 1–50 | Quantidade de capturas por exame |
| `total_time` | 10 | 1–120 s | Duração total do exame |
| Intervalo entre capturas | — | auto | `total_time / image_number` segundos |

#### Callbacks de `start_exam`

```python
session.start_exam(
    on_progress_callback=callable(captured, total),
    # Chamado a cada foto tirada — T4 usa para atualizar a barra de progresso

    on_capture_done_callback=callable(captured_images),
    # Chamado quando TODAS as fotos foram tiradas, ANTES da análise YOLO
    # T4 usa para trocar para T4b antes do processamento pesado

    on_finish_callback=callable(captured_images),
    # Chamado ao final de toda a análise YOLO
    # T4b usa para navegar para T5 (exame concluído)
)
```

#### Callbacks de análise registrados por T4b

Além dos callbacks de `start_exam`, a tela T4b registra callbacks diretamente na sessão:

```python
session._ui_analyze_progress_cb = callable(idx, total, fname)
# Chamado a cada imagem analisada pelo YOLO

session._ui_analyze_finish_cb = callable(captured_images)
# Chamado ao finalizar toda a análise
```

#### Atributo `last_analyzed_folder`

```python
session.last_analyzed_folder  # str — caminho absoluto da pasta do último exame
# Exibido pela tela T5 como confirmação do exame salvo
```

#### Fluxo interno de `_capture_loop`

```mermaid
flowchart TD
    A[start_exam chamado] --> B[session_ts = timestamp atual]
    B --> C[Thread de captura inicia]
    C --> D{captured < image_number?}
    D -- Sim --> E{Passou o intervalo?}
    E -- Não --> D
    E -- Sim --> F[camera.get_frame]
    F --> G["Salva YYYYMMDD_capture_N.jpg"]
    G --> H[on_progress_callback N/total]
    H --> D
    D -- Não --> I[on_capture_done_callback]
    I --> J[sleep 400ms — UI troca para T4b]
    J --> K[_analyze_all]
    K --> L[on_finish_callback]
```

#### Método `get_exam_gallery`

```python
exams = session.get_exam_gallery()
# Retorna lista de dicts, mais recente primeiro:
[{
    "name":       "Exame 04-09-26 - 23-48",
    "folder":     "/caminho/absoluto/Exame 04-09-26 - 23-48",
    "images":     ["/caminho/Analise 01.jpg", ...],
    "detections": {
        "Analise 01.jpg": [{"label": "normal", "conf": 0.9321}]
    }
}]
```

---

## 6. Módulo `ui.py` — Interface Gráfica

**Linhas:** 1697 | Construído com **CustomTkinter** sobre Tkinter puro.

> **Nota:** A docstring do topo de `ui.py` menciona "ESP32 HID" — isso é um resquício histórico. O controlador físico ativo é o **Raspberry Pi Pico 2W** (firmware `pico2w_hid_controller.ino`).

### 6.1 Modo de Operação — `TOUCH_MODE`

```python
# Topo de ui.py — linha ~53
TOUCH_MODE = True   # padrão atual: touchscreen
# TOUCH_MODE = False  # para operar via botões HID/teclado
```

| `TOUCH_MODE` | Impacto nas telas |
|---|---|
| `True` | Botões clicáveis em todas as telas; galeria com toque em cada item; botões ANTERIOR/PRÓXIMO no nível 3 |
| `False` | Nenhum botão tem `command`; toda navegação é via `handle_key()` |

### 6.2 Hierarquia de Telas

```mermaid
graph TD
    L[ScreenLoading] -- modelo pronto --> T0[ScreenT0\nCréditos / Institucional]
    T0 -- ENTER / botão --> T1[ScreenT1\nSplash / Menu Principal]
    T1 -- INICIAR --> T2[ScreenT2\nConfiguração Wizard]
    T1 -- GALERIA --> G[ScreenGaleria]
    T2 -- passo 2 OK --> T3[ScreenT3\nRevisão + Feed Câmera]
    T3 -- VOLTAR --> T2
    T3 -- INICIAR --> T4[ScreenT4\nCapturando...]
    T4 -- captura concluída --> T4b[ScreenT4b\nAnalisando YOLO...]
    T4b -- análise concluída --> T5[ScreenT5\nExame Concluído]
    T5 -- NOVO EXAME --> T1
    T5 -- GALERIA --> G
    G -- LEFT / botão VOLTAR --> T1 ou T5
```

> **Nota v1.1:** "NOVO EXAME" em T5 retorna para **T1** (menu principal), não para T2.

### 6.3 Classe Base — `BaseScreen`

Todas as telas herdam de `BaseScreen(ctk.CTkFrame)`, que fornece:

| Membro | Tipo | Descrição |
|--------|------|-----------|
| `self.app` | `VisualDetectUI` | Referência à janela principal |
| `self.session` | `CaptureSession` | Backend injetado pelo `VisualDetectUI` |
| `safe_after(ms, cb)` | método | Registra `after()` com cancelamento automático ao trocar de tela |
| `cleanup()` | método | Cancela todos os `after()` pendentes — chamado por `show_screen()` |
| `handle_key(event)` | método | Sobrescrito por cada tela para tratar input de teclado/HID |
| `_load_ctk_image(path, max_w, max_h)` | estático | Carrega PNG como `CTkImage` com fallback silencioso |

### 6.4 Paleta de Cores

```python
SCREEN_WIDTH  = 800
SCREEN_HEIGHT = 480
```

| Variável `C[...]` | Hex | Uso |
|-------------------|-----|-----|
| `bg` | `#0d0b1a` | Fundo principal |
| `bg_card` | `#1a1533` | Fundo de cards e painéis |
| `bg_card_light` | `#252040` | Cards secundários |
| `bg_field` | `#1e1940` | Fundo de campo de entrada |
| `border` | `#2d2755` | Bordas inativas |
| `border_active` | `#00e676` | Bordas de campo ativo |
| `green` | `#00e676` | Ações primárias, confirmações |
| `green_dark` | `#00c853` | Hover do verde primário |
| `amber` | `#ffc107` | Avisos, progresso de análise |
| `red` | `#ff1744` | Erros, indicador de captura ativa |
| `purple` | `#7c4dff` | Botões secundários |
| `purple_light` | `#b388ff` | Hover do roxo |
| `white` | `#ffffff` | Texto principal |
| `text2` | `#9e9ab8` | Texto secundário |
| `muted` | `#5c5880` | Texto de dica / inativo |
| `btn_off` | `#2a2550` | Fundo de botão inativo |
| `btn_off_border` | `#3d3670` | Borda de botão inativo |
| `black` | `#000000` | Texto sobre fundo verde |
| `transparent` | `"transparent"` | Frames sem cor de fundo |

### 6.5 Detalhamento por Tela

Cada tela é subclasse de `BaseScreen(ctk.CTkFrame)` e acessa o backend via `self.session`.

---

#### ScreenLoading

Exibida na inicialização enquanto o modelo YOLO carrega em background.

- Barra de progresso **indeterminada** com animação de pontos
- Ao receber `on_ready` do backend, exibe "Pronto!" e avança automaticamente para `T0`
- Nenhuma interação do usuário necessária

---

#### T0 — Créditos Institucionais

![T0 - Desenvolvedores](../interface/T0%20-%20Desenvolvedores.jpeg)

| | |
|--|--|
| **Tecla de saída** | `ENTER` |
| **Toque (TOUCH_MODE)** | Botão "CONTINUAR" |
| **Próxima tela** | T1 |

---

#### T1 — Splash / Menu Principal

![T1 - Tela Inicial](../interface/T1%20-%20Tela%20inicial.jpeg)

| | |
|--|--|
| **Seleção** | `sel = 0` (INICIAR) ou `sel = 1` (GALERIA) |
| **Navegação (HID)** | `↑/↓` muda seleção; `ENTER` confirma |
| **Toque (TOUCH_MODE)** | Clique direto nos botões |
| **Botão ativo** | Verde (INICIAR) ou Roxo (GALERIA) |

---

#### T2 — Configuração do Exame (Wizard 2 passos)

**Passo 0:** Número de capturas (`image_number`, 1–50)

![T2 - Número de Imagens](../interface/T2%20-%20Sela%C3%A7%C3%A3o%20de%20numero%20de%20imagens.jpeg)

**Passo 1:** Tempo total do exame (`total_time`, 1–120 s)

![T2.1 - Tempo Total](../interface/T2.1%20-%20Sele%C3%A7%C3%A3o%20de%20tempo%20total.jpeg)

| | |
|--|--|
| **Navegação (HID)** | `↑/↓` ajusta valor; `ENTER` avança passo; `←` volta passo ou tela |
| **Toque (TOUCH_MODE)** | Botões `−` / `+` dentro do card; botões "VOLTAR" / "PRÓXIMO" no footer |
| **Destino dos valores** | Salvos diretamente em `session.image_number` e `session.total_time` |

---

#### T3 — Revisão + Feed de Câmera

![T3 - Pré-exame](../interface/T3%20-%20Tela%20de%20inform%C3%A7%C3%B5es%20pr%C3%A9-exame.jpeg)

| | |
|--|--|
| **Navegação (HID)** | `←/→` alterna entre VOLTAR/INICIAR; `ENTER` confirma |
| **Toque (TOUCH_MODE)** | Botões "← VOLTAR" e "INICIAR →" clicáveis diretamente |
| **Feed ao vivo** | Câmera exibida em painel lateral — permite verificar posicionamento |
| **Câmera** | Reiniciada automaticamente se estava parada (ex.: voltando de T4b) |

---

#### T4 — Capturando

![T4 - Início do Exame](../interface/T4%20-%20Tela%20duerante%20o%20exame%20(0%25).jpeg)

![T4 - Meio do Exame](../interface/T4%20-%20Tela%20durante%20o%20exame%20(~50%25).jpeg)

![T4 - Final do Exame](../interface/T4%20-%20Tela%20durante%20o%20exame%20(~100%25).jpeg)

| | |
|--|--|
| **Botões** | **Todos bloqueados** durante captura |
| **Feed ao vivo** | Câmera exibida na coluna direita durante todo o exame |
| **Barra de capturas** | Atualizada via `on_progress_callback(captured, total)` |
| **Barra de tempo** | Atualizada a cada 50 ms via `_tick()` local |
| **Countdown** | Label "Próxima captura em: X.X s" atualizado localmente |
| **Indicador** | Ponto vermelho piscante (`*`) indica captura ativa |
| **Saída** | Automática ao completar todas as capturas → T4b |

---

#### T4b — Analisando (YOLO em background)

![T4b - Análise 0%](../interface/T5%20-%20Tela%20de%20analise%20das%20capturas(0%25).jpeg)

![T4b - Análise 100%](../interface/T5%20-%20Tela%20de%20analise%20das%20capturas(100%25).jpeg)

| | |
|--|--|
| **Botões** | **Todos bloqueados** durante análise |
| **Câmera** | **Parada** nesta tela para liberar CPU do Raspberry Pi |
| **Spinner** | Animação `| / — \` em âmbar; vira `v` verde ao concluir |
| **Callbacks** | Registra `_ui_analyze_progress_cb` e `_ui_analyze_finish_cb` na sessão |
| **Label do arquivo** | Atualizado a cada imagem: "Analisando: Analise NN..." |
| **Saída** | Automática 1200 ms após `on_finish_callback` → T5 |

---

#### T5 — Exame Concluído

![T5 - Exame Concluído](../interface/T6%20-%20Tela%20de%20exame%20concluido.jpeg)

| | |
|--|--|
| **Seleção** | `NOVO EXAME` ou `VER GALERIA` |
| **Navegação (HID)** | `←/→` muda seleção; `ENTER` confirma |
| **Toque (TOUCH_MODE)** | Botões clicáveis diretamente |
| **Pasta do exame** | Nome de `session.last_analyzed_folder` exibido na tela |
| **NOVO EXAME** | Limpa `captured_images` e vai para **T1** (menu principal) |

> **Nota v1.2 — HID em TOUCH_MODE:** O `handle_key()` de T5 faz `return` imediatamente se `TOUCH_MODE = True`, tornando todas as teclas inativas nessa tela quando em modo touch. O mesmo se aplica à Galeria.

---

#### Galeria — Biblioteca de Exames (3 níveis)

**Nível 1 — Lista de exames:**

![Galeria - Seleção de Exame](../interface/T7%20-%20Tela%20galeria%20sele%C3%A7%C3%A3o%20de%20exame.jpeg)

**Nível 2 — Lista de capturas do exame:**

![Galeria - Seleção de Captura](../interface/T8%20-%20tela%20galeria%20sele%C3%A7%C3%A3o%20de%20captura.jpeg)

| Nível | Conteúdo | Navegação HID | Navegação Touch |
|-------|----------|---------------|-----------------|
| 1 | Pastas `Exame DD-MM-YY - HH-MM` | `↑/↓` navega; `ENTER` abre; `←` volta para T1/T5 | Toque no item; botão "← VOLTAR" no header |
| 2 | Imagens `Analise NN.jpg` com preview de detecção | `↑/↓` navega; `ENTER` abre; `←` volta nível 1 | Toque no item; botão "← VOLTAR" no header |
| 3 | Imagem anotada + detecções YOLO | `↑/↓` navega entre imagens; `←` volta nível 2 | Botões "◀ ANTERIOR" / "PRÓXIMO ▶"; botão "← VOLTAR" no header |

> **Novo v1.1:** Botão "← VOLTAR" permanente no header (TOUCH_MODE) e navegação entre imagens no nível 3 (`↑/↓` HID ou botões touch).

---

## 7. Fluxo Completo de um Exame

```mermaid
flowchart TD
    A([Equipamento ligado]) --> B[ScreenLoading\ncarrega modelo YOLO]
    B --> C[T0 — Créditos]
    C -- ENTER / CONTINUAR --> D[T1 — Menu Principal]
    D -- INICIAR --> E["T2 — Configuração\nnúmero de capturas + tempo"]
    D -- GALERIA --> K[Galeria]
    E -- confirma --> F[T3 — Revisão + feed câmera]
    F -- VOLTAR --> E
    F -- INICIAR --> G["T4 — Capturando\nbarra de progresso + feed ao vivo"]
    G -- todas as fotos tiradas --> H["T4b — Analisando\ncâmera parada; YOLO processa"]
    H -- análise concluída --> I["T5 — Exame Concluído\nnome da pasta exibido"]
    I -- NOVO EXAME --> D
    I -- GALERIA --> K
    K -- VOLTAR --> D ou I
```

---

## 8. Comunicação entre Threads

O sistema opera com **3 threads simultâneas** + thread principal da UI:

```mermaid
sequenceDiagram
    participant UI as Thread UI (Tkinter)
    participant CT as Thread Câmera
    participant YT as Thread YOLO/Captura

    Note over UI,YT: Fase: Carregamento
    UI->>YT: load_async(on_ready)
    YT->>YT: YOLO(model_path)
    YT->>UI: after(0, on_ready)

    Note over UI,YT: Fase: Captura (T4)
    UI->>CT: get_frame() com Lock
    UI->>UI: cv2.imwrite(fname)
    UI->>UI: after(0, on_progress)

    Note over UI,YT: Fase: Análise YOLO (T4b)
    CT->>CT: camera.stop() — câmera parada
    YT->>YT: YOLO.predict() x N imagens
    YT->>UI: after(0, on_analyze_progress)
    YT->>UI: after(0, on_finish)
```

> **Regra de ouro:** Toda chamada que modifica widgets Tkinter a partir de thread secundária deve usar `self.app.after(0, lambda: ...)`. O método `safe_after()` de `BaseScreen` facilita e registra os IDs para cancelamento ao trocar de tela.

---

## 9. Sistema de Arquivos Gerados

### Capturas brutas

```
app/capturas_voluntarios_analisar/
├── 20260904_234800_capture_1.jpg
├── 20260904_234800_capture_2.jpg
└── ...
```

Formato: `YYYYMMDD_HHMMSS_capture_N.jpg`

### Análises YOLO

```
app/capturas_analisadas_voluntarios/
└── Exame 04-09-26 - 23-48/
    ├── Analise 01.jpg          ← imagem original + bounding boxes YOLO
    ├── Analise 02.jpg
    └── detections.json
```

### Estrutura do `detections.json`

```json
{
  "Analise 01.jpg": [
    { "label": "normal",   "conf": 0.9321 },
    { "label": "anomalia", "conf": 0.0432 }
  ],
  "Analise 02.jpg": [],
  "Analise 03.jpg": [
    { "label": "anomalia", "conf": 0.8754 }
  ]
}
```

- `label`: classe detectada pelo YOLO
- `conf`: confiança (0.0–1.0, 4 casas decimais)
- Lista vazia → nenhuma detecção nessa imagem

---

## 10. Firmware — pico2w_hid_controller

**Arquivo:** `firmware/pico2w_hid_controller/pico2w_hid_controller.ino`
**Hardware:** Raspberry Pi Pico 2W (chip RP2350 — ARM Cortex-M33)
**Ambiente:** Arduino IDE + core `arduino-pico` (earlephilhower)

### 10.1 Hardware e Pinagem

| GPIO | Função | Tecla HID | Ação no VisualDetect |
|------|--------|-----------|----------------------|
| 5 | Botão Direita | `RIGHT_ARROW` | Próximo item / avançar |
| 6 | Botão Esquerda | `LEFT_ARROW` | Item anterior / voltar |
| 7 | Botão Cima | `UP_ARROW` | Aumentar valor / item acima |
| 8 | Botão Baixo | `DOWN_ARROW` | Diminuir valor / item abaixo |
| 9 | Botão Enter | `RETURN` | Confirmar / abrir |

> Todos os pinos usam `INPUT_PULLUP`. Conecte o botão entre o GPIO e o **GND**. Nenhum resistor externo é necessário.

#### Diagrama de conexão

```
  GPIO 5 ──[ Botão DIREITA ]── GND
  GPIO 6 ──[ Botão ESQUERDA]── GND
  GPIO 7 ──[ Botão CIMA    ]── GND
  GPIO 8 ──[ Botão BAIXO   ]── GND
  GPIO 9 ──[ Botão ENTER   ]── GND

  Pico 2W ──USB──► Raspberry Pi 4
  (reconhecido pelo SO como teclado HID genérico — sem drivers)
```

### 10.2 Lógica do Firmware

#### Loop principal com debounce por tempo

```mermaid
flowchart TD
    A[loop] --> B[Para cada botão i]
    B --> C[currentState = digitalRead GPIO_i]
    C --> D{"currentState == LOW\nAND lastState == HIGH?"}
    D -- Não --> G[lastState = currentState]
    D -- Sim --> E{"now - lastDebounce >= 30ms?"}
    E -- Não --> G
    E -- Sim --> F["lastDebounce = now\nKeyboard.press key_i\ndelay 15ms\nKeyboard.release key_i"]
    F --> G
    G --> H[delay 5ms]
    H --> A
```

| Parâmetro | Valor | Descrição |
|-----------|-------|-----------|
| `DEBOUNCE_MS` | 30 ms | Intervalo mínimo entre detecções do mesmo botão |
| Pulso de tecla | 15 ms | Duração do `press` antes do `release` |
| Delay de loop | 5 ms | Cadência de leitura dos GPIOs |

### 10.3 Configuração do Arduino IDE

| Configuração | Valor |
|-------------|-------|
| Board Manager URL | `https://github.com/earlephilhower/arduino-pico/releases/download/global/package_rp2040_index.json` |
| Placa | Raspberry Pi Pico 2 W |
| USB Stack | TinyUSB |

### 10.4 Gravação do Firmware

#### Primeira gravação (modo BOOTSEL)

```
1. Segure o botão BOOTSEL no Pico
2. Conecte o cabo USB ao computador enquanto segura BOOTSEL
3. Solte BOOTSEL — o Pico monta como pendrive (RPI-RP2)
4. No Arduino IDE, clique em Upload
```

#### Gravações subsequentes

Após a primeira gravação, basta clicar em **Upload** normalmente pelo Arduino IDE — sem modo BOOTSEL.

#### Debug serial (115200 baud)

```
=== Pico 2W HID Controller ===
Aguardando pressao de botoes...
[HID] Botao GPIO 5 -> Seta Direita (Right)
[HID] Botao GPIO 9 -> Enter        (Return)
```

---

## 11. Integração Hardware-Software

```mermaid
graph TD
    B1["Botão Direita\nGPIO 5"] --> P
    B2["Botão Esquerda\nGPIO 6"] --> P
    B3["Botão Cima\nGPIO 7"] --> P
    B4["Botão Baixo\nGPIO 8"] --> P
    B5["Botão Enter\nGPIO 9"] --> P

    P["Raspberry Pi Pico 2W\nFirmware HID\n(TinyUSB)"] -- "USB — HID Keyboard" --> R

    R["Raspberry Pi 4\nLinux"] -- "KeyPress event" --> A

    A["app/ui.py\nhandle_key(event)"] --> TL["Tela atual\nresponde ao input"]

    style P fill:#1a1533,color:#00e676,stroke:#00e676
    style R fill:#1a1533,color:#fff,stroke:#2d2755
    style A fill:#252040,color:#fff,stroke:#7c4dff
```

O Pico 2W é **completamente transparente** para o SO: o Raspberry Pi 4 o vê como teclado USB genérico — sem drivers adicionais, sem `udev`, sem permissões especiais.

> **Nota:** Com `TOUCH_MODE = True`, o controlador HID ainda funciona em T0, T1, T2 e T3 (que não fazem `return` antecipado no `handle_key()`). Em T5 e Galeria, `handle_key()` faz `return` imediatamente quando `TOUCH_MODE = True`, ignorando todo input de teclado nessas telas.

> **Deploy:** Para instruções completas de instalação no Raspberry Pi, configuração do autostart (systemd) e resolução de problemas, consulte [`docs/dev/INSTALL_RASPBERRY.md`](INSTALL_RASPBERRY.md).

---

## 12. Dependências e Requisitos

### Software (PC / desenvolvimento)

```bash
# requirements_pc.txt
customtkinter
opencv-python
ultralytics
pillow
```

```bash
# Instalação
python -m venv .venv
.venv\Scripts\activate        # Windows
source .venv/bin/activate     # Linux/Mac
pip install -r requirements_pc.txt
```

### Software (Raspberry Pi — versões fixas)

```bash
# requirements_rpi.txt — versões testadas e fixas para o Raspberry Pi 4
# Última atualização: 2026-09-09
ultralytics==8.4.126
opencv-python==5.0.0.93
numpy==2.4.6
Pillow==12.3.0
customtkinter==6.0.0
```

```bash
# Pré-requisito: PyTorch CPU-only (instalar ANTES do requirements_rpi.txt)
pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu
pip install -r requirements_rpi.txt

# Dependências do sistema (via apt-get):
sudo apt install python3-tk python3-dev
sudo apt install libgl1 libglib2.0-0 libsm6 libxext6 libxrender-dev
```

### Hardware mínimo

| Componente | Especificação |
|------------|---------------|
| Computador | Raspberry Pi 4 (2 GB RAM mín.) ou PC x86 |
| Câmera | Webcam USB (compatível com OpenCV, índice `0` padrão) |
| Controlador | Raspberry Pi Pico 2W com firmware gravado (opcional em TOUCH_MODE) |
| Tela | Display HDMI 800×480 mínimo (touch recomendado para TOUCH_MODE) |
| Modelo YOLO | `app/models/best.pt` (não incluso no repositório) |

---

## 13. Configurações e Parâmetros Ajustáveis

### `main.py`

| Constante | Padrão | Como alterar |
|-----------|--------|--------------|
| `MODELO_PATH` | `app/models/best.pt` | Substitua `best.pt` pelo nome do seu `.pt` |
| `CAPTURE_FOLDER` | `app/capturas_voluntarios_analisar` | Mude o nome da pasta |
| `ANALYZED_FOLDER` | `app/capturas_analisadas_voluntarios` | Mude o nome da pasta |

### `ui.py`

| Constante | Padrão | Descrição |
|-----------|--------|-----------|
| `SCREEN_WIDTH` | `800` | Largura da janela em pixels |
| `SCREEN_HEIGHT` | `480` | Altura da janela em pixels |
| `TOUCH_MODE` | `True` | `True` = touchscreen; `False` = HID/teclado |
| `C["green"]` | `#00e676` | Cor primária — altere para rebranding |
| `C["purple"]` | `#7c4dff` | Cor secundária |

### `backend.py`

| Constante | Padrão | Descrição |
|-----------|--------|-----------|
| `CAPTURE_FOLDER_DEFAULT` | `capturas_voluntarios_analisar` | Usado se `main.py` não passar pasta |
| `ANALYZED_FOLDER_DEFAULT` | `capturas_analisadas_voluntarios` | Idem |
| `image_number` | `10` | Capturas por exame (ajustado em T2) |
| `total_time` | `10` | Segundos de exame (ajustado em T2) |

### `pico2w_hid_controller.ino`

| Constante | Padrão | Descrição |
|-----------|--------|-----------|
| `DEBOUNCE_MS` | `30` | Intervalo mínimo entre detecções (ms) |
| Pulso de tecla | `15 ms` | Duração do `press` antes do `release` |
| `BUTTONS[]` | `{5, 6, 7, 8, 9}` | GPIOs dos botões |

---

## 14. Navegação por Teclado / HID

> Aplicável quando `TOUCH_MODE = False`. Com `TOUCH_MODE = True`, as teclas ainda são processadas em T0, T1, T2, T3 e nos níveis 1–3 da Galeria (em modo HID).

O `VisualDetectUI` captura eventos de teclado globalmente e despacha para a tela ativa via `handle_key(event)`.

### Mapeamento completo por tela

| Tela | `←` Left | `→` Right | `↑` Up | `↓` Down | `ENTER` |
|------|----------|-----------|--------|----------|---------|
| **T0** | — | — | — | — | Avança para T1 |
| **T1 Splash** | — | — | Seleciona INICIAR | Seleciona GALERIA | Confirma seleção |
| **T2 Config** | Volta passo / tela | — | Aumenta valor | Diminui valor | Avança passo / confirma |
| **T3 Revisão** | Seleciona VOLTAR | Seleciona INICIAR | — | — | Confirma seleção |
| **T4 Capturando** | 🔒 | 🔒 | 🔒 | 🔒 | 🔒 |
| **T4b Analisando** | 🔒 | 🔒 | 🔒 | 🔒 | 🔒 |
| **T5 Concluído** | Seleciona NOVO EXAME | Seleciona GALERIA | — | — | Confirma seleção |
| **Galeria Nível 1** | Volta para T1/T5 | — | Item acima | Item abaixo | Abre exame |
| **Galeria Nível 2** | Volta nível 1 | — | Item acima | Item abaixo | Abre imagem |
| **Galeria Nível 3** | Volta nível 2 | — | Imagem anterior | Próxima imagem | — |

> O teclado físico e o controlador Pico 2W HID usam exatamente as mesmas teclas — o sistema não distingue a origem do input.

---

## 15. Modo Touchscreen (TOUCH_MODE)

O `TOUCH_MODE` foi introduzido na versão 1.1 para suportar displays touchscreen sem o controlador HID físico.

### O que muda com `TOUCH_MODE = True`

| Tela | Mudança |
|------|---------|
| **T0** | Exibe botão "CONTINUAR" em vez do texto de hint de teclado |
| **T1** | Botões INICIAR e GALERIA são clicáveis diretamente |
| **T2** | Botões `−` / `+` dentro do card; footer com "VOLTAR" / "PRÓXIMO" |
| **T3** | Botões "← VOLTAR" e "INICIAR →" clicáveis; hint de toque |
| **T5** | Botões "NOVO EXAME" e "VER GALERIA" clicáveis; hint de toque |
| **Galeria** | Botão "← VOLTAR" permanente no header; toque em itens nos níveis 1 e 2; botões "◀ ANTERIOR" / "PRÓXIMO ▶" no nível 3 |

### Como alternar modos

Edite a constante no topo de `app/ui.py`:

```python
TOUCH_MODE = True   # touchscreen (padrão atual)
TOUCH_MODE = False  # HID/teclado físico
```

Não é necessário reiniciar o ambiente — basta reiniciar a aplicação.

---

## 16. Deploy e Autostart (Raspberry Pi)

Para o guia completo de instalação, deploy e configuração do autostart via `systemd`, consulte:

📄 [`docs/dev/INSTALL_RASPBERRY.md`](INSTALL_RASPBERRY.md)

O documento cobre:
- Clonagem do repositório e configuração de branch `raspberry-pi`
- Instalação via script automático (`install_rpi.sh`) ou passo a passo
- Configuração do autostart com `visualdetect.service`
- Transferência do modelo `.pt` para o dispositivo
- Comandos do dia a dia e resolução de problemas

---

*Documentação atualizada em Outubro de 2026 · Versão 1.2. Para atualizações, edite este arquivo e faça commit no repositório `MYuri-beck/visual-detect`.*
