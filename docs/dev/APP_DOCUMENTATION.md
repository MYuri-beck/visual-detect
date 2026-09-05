# 📘 Documentação da Pasta `app/` — VisualDetect

> **Versão:** 1.0  
> **Projeto:** VisualDetect — Equipamento de Triagem do Reflexo Ocular  
> **Autores:** Yuri Mendes | Andrei Krug  

---

## Índice

1. [Visão Geral](#1-visão-geral)
2. [Estrutura de Arquivos](#2-estrutura-de-arquivos)
3. [Arquitetura do Sistema](#3-arquitetura-do-sistema)
4. [main.py — Ponto de Entrada](#4-mainpy--ponto-de-entrada)
5. [backend.py — Camada de Lógica](#5-backendpy--camada-de-lógica)
6. [ui.py — Interface Gráfica](#6-uipy--interface-gráfica)
7. [Fluxo Completo de um Exame](#7-fluxo-completo-de-um-exame)
8. [Comunicação entre Threads](#8-comunicação-entre-threads)
9. [Sistema de Arquivos Gerados](#9-sistema-de-arquivos-gerados)
10. [Dependências e Requisitos](#10-dependências-e-requisitos)
11. [Configurações e Personalização](#11-configurações-e-personalização)
12. [Navegação pelo Teclado / HID ESP32](#12-navegação-pelo-teclado--hid-esp32)

---

## 1. Visão Geral

O **VisualDetect** é um software embarcado desenvolvido para triagem do reflexo ocular utilizando visão computacional. A aplicação roda em um **Raspberry Pi** (ou PC para desenvolvimento) e executa o seguinte fluxo:

1. Captura automática de frames da câmera durante um exame
2. Análise de cada imagem com um modelo **YOLO** treinado para detectar anomalias oculares
3. Armazenamento das imagens anotadas organizadas por data/hora do exame
4. Galeria para revisão dos exames anteriores

**Tecnologias utilizadas:**

| Tecnologia | Função |
|---|---|
| Python 3.11 | Linguagem base |
| OpenCV (`cv2`) | Captura de câmera e processamento de imagens |
| Ultralytics YOLO | Modelo de visão computacional para detecção |
| CustomTkinter (`ctk`) | Interface gráfica moderna (dark mode) |
| Pillow (PIL) | Exibição de imagens na UI |
| Threading | Paralelismo câmera + UI + análise YOLO |

---

## 2. Estrutura de Arquivos

```
app/
├── main.py                          # Ponto de entrada da aplicação
├── backend.py                       # Lógica de câmera, YOLO e sessão de exame
├── ui.py                            # Interface gráfica (todas as telas)
│
├── assets/                          # Recursos visuais
│   ├── logo - VisualDetect_greenPupil_png-Photoroom.png   # Logo principal (Splash)
│   ├── logo - VisualDetect.png
│   ├── logo - VisualDetect_png.png
│   ├── logo - NUDEP_branco_png.png
│   └── logo - NUDEP_png.png
│
├── models/
│   └── best.pt                      # Modelo YOLO treinado (não incluso no repo)
│
├── capturas_voluntarios_analisar/   # Imagens brutas capturadas durante exames
│   └── YYYYMMDD_HHMMSS_capture_N.jpg
│
└── capturas_analisadas_voluntarios/ # Imagens com anotações YOLO por exame
    └── Exame DD-MM-YY - HH-MM/
        ├── Analise 01.jpg
        ├── Analise 02.jpg
        └── detections.json
```

---

## 3. Arquitetura do Sistema

```
┌──────────────────────────────────────────────────────────┐
│                      main.py                             │
│  (configura caminhos, instancia backend, entrega para UI)│
└───────────────────────────┬──────────────────────────────┘
                            │ injeção de dependência
                            ▼
┌──────────────────────────────────────────────────────────┐
│                   CaptureSession                         │
│  ┌────────────────┐    ┌──────────────────────────────┐  │
│  │ CameraManager  │    │      VisionAnalyzer          │  │
│  │ Thread Câmera  │    │  YOLO (carregado async)      │  │
│  │ ~30 FPS        │    │  analyze_file() + JSON       │  │
│  └────────────────┘    └──────────────────────────────┘  │
└───────────────────────────┬──────────────────────────────┘
                            │ session injetada
                            ▼
┌──────────────────────────────────────────────────────────┐
│               VisualDetectUI (ui.py)                     │
│  Loading → T0 → T1 → T2 → T3 → T4 → T4b → T5 → Galeria │
│  (cada tela é um CTkFrame independente)                  │
└──────────────────────────────────────────────────────────┘
```

**Princípios de design:**
- **Separação total** entre backend e UI — `backend.py` não importa nada de `ui.py` e vice-versa
- **Injeção de dependência** — a `CaptureSession` é criada em `main.py` e entregue para a UI
- **Thread safety** — toda atualização de widget vinda de thread usa `after(0, callback)`

---

## 4. `main.py` — Ponto de Entrada

**Linhas:** 95

### Responsabilidades

- Define os caminhos de configuração (modelo, pastas de captura e análise)
- Instancia os objetos do backend na ordem correta
- Configura o tema do CustomTkinter
- Inicia o loop principal do Tkinter
- Garante o encerramento limpo da câmera ao fechar

### Configurações editáveis

```python
MODELO_PATH     = os.path.join(_APP_DIR, "models", "best.pt")
CAPTURE_FOLDER  = os.path.join(_APP_DIR, "capturas_voluntarios_analisar")
ANALYZED_FOLDER = os.path.join(_APP_DIR, "capturas_analisadas_voluntarios")
```

### Sequência de inicialização

```python
camera   = CameraManager()          # 1. Cria gerenciador de câmera
camera.start()                      # 2. Inicia captura em thread
analyzer = VisionAnalyzer(path)     # 3. Prepara analisador YOLO (não carrega ainda)
session  = CaptureSession(...)      # 4. Cria sessão com câmera + analisador
ctk.set_appearance_mode("dark")     # 5. Configura tema da UI
app = VisualDetectUI(session)       # 6. Inicia UI com sessão injetada
app.mainloop()                      # 7. Loop principal (bloqueia aqui)
camera.stop()                       # 8. Encerramento limpo
```

### Como rodar

```bash
python main.py              # janela 800x480
python main.py --fullscreen # tela cheia (Raspberry Pi)
python main.py -f           # equivalente ao acima
```

---

## 5. `backend.py` — Camada de Lógica

**Linhas:** 419

Não importa nada de outros módulos do projeto. Dependências com **graceful degradation**:

```python
CV2_AVAILABLE  = True  # False se opencv não estiver instalado
YOLO_AVAILABLE = True  # False se ultralytics não estiver instalado
```

---

### `CameraManager`

Gerencia a câmera em **thread separada** para não bloquear a UI.

#### Métodos públicos

| Método | Retorno | Descrição |
|---|---|---|
| `start(index=1)` | `bool` | Abre câmera e inicia thread. `index=0` webcam integrada, `index=1` USB externa |
| `stop()` | — | Para thread e libera hardware |
| `get_frame()` | `ndarray \| None` | Retorna frame BGR mais recente (thread-safe) |
| `available` | `bool` | `True` se câmera está aberta e pronta |

#### Funcionamento interno

```
Thread Principal (UI)            Thread da Câmera (_loop)
       │                                    │
       │  get_frame() ──── Lock ────────────│
       │  ← retorna cópia do _frame         │  cap.read() → flip → _frame
                                            │  time.sleep(0.033) ~30 FPS
```

- Frame espelhado horizontalmente (`cv2.flip(frame, 1)`)
- Buffer protegido por `threading.Lock()`
- Retorna **cópia** do frame (não referência)

---

### `VisionAnalyzer`

Carrega e executa o modelo YOLO.

#### Métodos públicos

| Método | Descrição |
|---|---|
| `load_sync()` | Carrega o modelo bloqueando a thread chamadora |
| `load_async(on_ready=None)` | Carrega em background; chama `on_ready()` quando terminar |
| `analyze_file(image_path, output_path)` | Analisa imagem, salva resultado anotado, retorna lista de detecções |
| `available` | `True` se modelo foi carregado com sucesso |
| `is_loading` | `True` enquanto carregando |

#### Retorno de `analyze_file`

```python
[("normal", 0.9321), ("anomalia", 0.7854)]
# Retorna [] se modelo indisponível ou erro
```

#### Fluxo de carregamento assíncrono

```
ScreenLoading (UI)              Thread Worker
      │  load_async(on_ready=cb) ──────────► YOLO(model_path)
      │  UI continua animando...             modelo carregado
      │◄── after(0, cb) ────────────────────
      │  avança para T0 automaticamente
```

---

### `CaptureSession`

Coordena o fluxo completo de um exame.

#### Parâmetros de exame

```python
session.image_number = 10   # Qtd de capturas por exame (1–50)
session.total_time   = 10   # Duração total em segundos (1–120)
# Intervalo calculado automaticamente: total_time / image_number
```

#### Método `start_exam`

```python
session.start_exam(
    on_finish_callback=None,        # callable(images) — fim da análise YOLO
    on_progress_callback=None,      # callable(captured, total) — a cada foto
    on_capture_done_callback=None,  # callable(images) — todas as fotos tiradas,
                                    # ANTES da análise YOLO começar
)
```

> **`on_capture_done_callback`** é chamado entre a captura e a análise YOLO. A UI usa isso para trocar de **T4 → T4b** antes do processamento pesado.

#### Callbacks de análise (registrados dinamicamente por T4b)

```python
session._ui_analyze_progress_cb = callable(idx, total, fname)
session._ui_analyze_finish_cb   = callable(captured_images)
```

#### Método `_analyze_all` (interno)

1. Cria subpasta `ANALYZED_FOLDER/Exame DD-MM-YY - HH-MM/`
2. Para cada imagem: chama `analyzer.analyze_file()`, salva `Analise NN.jpg`
3. Gera `detections.json` com todas as detecções

#### Método `get_exam_gallery`

```python
exams = session.get_exam_gallery()
# Retorna lista de dicts (mais recente primeiro):
[{
    "name":       "Exame 02-09-26 - 14-35",
    "folder":     "/caminho/absoluto/Exame 02-09-26 - 14-35",
    "images":     ["/caminho/Analise 01.jpg", ...],
    "detections": {"Analise 01.jpg": [{"label": "normal", "conf": 0.93}]}
}]
```

---

## 6. `ui.py` — Interface Gráfica

**Linhas:** 1461

### Configuração Visual

```python
SCREEN_WIDTH  = 800   # resolução da janela
SCREEN_HEIGHT = 480
```

**Paleta de cores (dicionário `C`):**

| Chave | Hex | Uso |
|---|---|---|
| `bg` | `#0d0b1a` | Fundo principal |
| `bg_card` | `#1a1533` | Cards e painéis |
| `bg_card_light` | `#252040` | Cards secundários |
| `border` | `#2d2755` | Bordas inativas |
| `border_active` | `#00e676` | Bordas ativas |
| `green` | `#00e676` | Destaque principal |
| `amber` | `#ffc107` | Cor da análise YOLO |
| `red` | `#ff1744` | Indicador de gravação |
| `purple` | `#7c4dff` | Botão Galeria |
| `text2` | `#9e9ab8` | Textos secundários |
| `muted` | `#5c5880` | Textos apagados |

---

### `BaseScreen`

Classe base da qual todas as telas herdam:

```python
class BaseScreen(ctk.CTkFrame):
    self.app      # referência à janela principal
    self.session  # CaptureSession injetada

    safe_after(ms, callback)  # after() com cancelamento automático
    cleanup()                 # cancela todos os after() pendentes
    handle_key(event)         # sobrescrito em cada tela
    _load_ctk_image(path, max_w, max_h)  # carrega PNG como CTkImage
```

> **Por que `safe_after`?** Ao trocar de tela, a tela anterior é destruída. `safe_after` rastreia e cancela todos os `after()` em `cleanup()` para evitar chamadas a widgets inexistentes.

---

### `VisualDetectUI` (Aplicação Principal)

Janela principal (`ctk.CTk`). Gerencia navegação entre telas.

```python
SCREENS = {
    "loading": ScreenLoading,  "t0": ScreenT0,
    "t1":  ScreenT1,           "t2": ScreenT2,
    "t3":  ScreenT3,           "t4": ScreenT4,
    "t4b": ScreenT4b,          "t5": ScreenT5,
    "galeria": ScreenGaleria,
}

show_screen(name)   # destroi tela atual, instancia e exibe a nova
start_exam()        # navega para T4
new_exam()          # limpa sessão, volta para T1
```

| Tecla Global | Ação |
|---|---|
| `ESC` | Sai do fullscreen ou fecha app |
| `F11` | Alterna fullscreen |
| Qualquer tecla | Repassada para `current_screen.handle_key(event)` |

---

### Telas (Screens)

#### `ScreenLoading` — Carregando Modelo

- Dispara `analyzer.load_async()` imediatamente
- Anima texto com pontinhos a cada 400ms
- Avança automaticamente para `T0` após 600ms do carregamento
- **Input:** bloqueado

---

#### `ScreenT0` — Informações Institucionais

- Exibe autores do projeto
- **Input:** `ENTER` → `T1`

---

#### `ScreenT1` — Splash / Menu Principal

```
[Logo VisualDetect]
 VISUAL DETECT
 Triagem do Reflexo Ocular

 [ INICIAR ]   ← verde (selecionado)
 [ GALERIA ]
```

- **Input:** `↑`/`↓` alterna seleção; `ENTER` confirma

---

#### `ScreenT2` — Configuração (Wizard)

| Passo | Campo | Min | Max | Padrão |
|---|---|---|---|---|
| 0 | Nº de Capturas | 1 | 50 | 10 |
| 1 | Tempo Total (s) | 1 | 120 | 10 |

- Valores gravados diretamente em `session.image_number` e `session.total_time`
- Flash verde de feedback visual ao ajustar
- **Input:** `↑`/`↓` ajusta; `ENTER` avança/confirma; `←` volta

---

#### `ScreenT3` — Revisão + Feed da Câmera

Layout em 2 colunas:
- **Esquerda:** resumo de capturas, tempo e intervalo calculado
- **Direita:** feed ao vivo da câmera (50ms de refresh, aspect ratio preservado)

> Se a câmera estava parada (vinda da análise YOLO), **T3 a reinicia automaticamente**.

- **Input:** `←`/`→` seleciona botão; `ENTER` confirma

---

#### `ScreenT4` — Capturando

- Exibe barra de progresso de capturas e tempo
- Ponto vermelho piscante (500ms)
- Countdown para próxima foto
- Feed ao vivo da câmera
- **Input:** completamente bloqueado

**Início da captura:**
```python
def start_capture():
    session.start_exam(
        on_progress_callback    = self._on_progress,
        on_capture_done_callback = lambda imgs: self.after(0, self._go_to_t4b),
    )
```

---

#### `ScreenT4b` — Analisando (YOLO)

- **Câmera é parada** para liberar CPU do Raspberry Pi
- Registra callbacks de progresso na sessão
- Spinner `|`/`/`/`—`/`\` animado a cada 150ms
- Barra de progresso ambar
- **Input:** completamente bloqueado
- Ao terminar: feedback verde → aguarda 1.2s → navega para `T5`

**Registro de callbacks:**
```python
session._ui_analyze_progress_cb = self._on_progress_thread
session._ui_analyze_finish_cb   = lambda imgs: self.after(0, self._on_finish)
```

---

#### `ScreenT5` — Exame Concluído

```
      (✓)
   EXAME CONCLUÍDO
 10 imagens capturadas e analisadas
 Pasta: Exame 02-09-26 - 14-35
 ─────────────────────────────────
  Retire o aparelho do paciente

 [NOVO EXAME]    [VER GALERIA]
```

- **Input:** `←`/`→` seleciona; `ENTER` confirma

---

#### `ScreenGaleria` — Biblioteca de Exames

**3 níveis de navegação:**

```
Nível 1: Lista de Exames
  > Exame 02-09-26 - 14-35  (10 análises)
    Exame 01-09-26 - 10-20  (8 análises)
    
        ↓ ENTER

Nível 2: Imagens do Exame
  > Analise 01    NORMAL 93.2%
    Analise 02    ANOMALIA 78.5%
    Analise 03    Sem detecção

        ↓ ENTER

Nível 3: Visualização
  NORMAL 93.2%
  ┌─────────────────────┐
  │ [imagem anotada YOLO│
  └─────────────────────┘
  [1 / 10]
```

**Detalhes técnicos:**
- Área de conteúdo reconstruída a cada mudança de nível (`_clear_content()`)
- Header e footer persistentes entre os 3 níveis
- Imagem carregada via `safe_after(60)` para aguardar widget ser renderizado
- Retorno à tela de origem via `app._gallery_origin` (`"t1"` ou `"t5"`)

---

## 7. Fluxo Completo de um Exame

```
[LOADING] ──── YOLO carregado ──► [T0] ─ ENTER ─► [T1]
                                                    │
                                             ENTER (INICIAR)
                                                    │
                                                   [T2]
                                             Configura capturas
                                             e tempo total
                                                    │ ENTER
                                                   [T3]
                                             Revisão + feed câmera
                                                    │ ENTER (INICIAR)
                                                    │
                         ┌─────────────────────────[T4]─────────────────────────┐
                         │           CAPTURANDO (câmera ligada)                  │
                         │  Foto 1 ... Foto N (interval = total_time/n_capturas) │
                         └──────────── on_capture_done ──────────────────────────┘
                                                    │
                         ┌─────────────────────────[T4b]────────────────────────┐
                         │           ANALISANDO (câmera desligada)               │
                         │  YOLO processa cada foto → salva + detections.json   │
                         └──────────── on_finish ─────────────────────────────── ┘
                                                    │
                                                   [T5]
                                            EXAME CONCLUÍDO
                                           /               \
                                    NOVO EXAME          VER GALERIA
                                        │                    │
                                       [T1]             [GALERIA]
```

---

## 8. Comunicação entre Threads

| Thread | Responsabilidade |
|---|---|
| **Main Thread** | Loop do Tkinter, atualiza widgets |
| **Thread da Câmera** | `CameraManager._loop()` — frames contínuos |
| **Thread do Backend** | `CaptureSession._capture_loop()` — captura + YOLO |

### Regra fundamental do Tkinter

> **Nunca atualizar widgets de fora da main thread.**

```python
# Errado (em thread secundária):
self._lbl.configure(text="5 / 10")   # ❌ crash potencial

# Correto:
self.after(0, lambda: self._lbl.configure(text="5 / 10"))  # ✅
```

### Acesso thread-safe ao frame da câmera

```python
# CameraManager usa Lock + retorna cópia:
with self._lock:
    return self._frame.copy()  # cópia, não referência
```

### Tempo de espera entre captura e análise

```python
# backend.py — _capture_loop()
time.sleep(0.4)  # 400ms para UI trocar para T4b e registrar callbacks
# Só então inicia a análise YOLO
```

---

## 9. Sistema de Arquivos Gerados

### Capturas brutas

```
app/capturas_voluntarios_analisar/
├── 20260902_143510_capture_1.jpg
├── 20260902_143510_capture_2.jpg
└── ...
```
Formato: `YYYYMMDD_HHMMSS_capture_N.jpg`

### Imagens analisadas

```
app/capturas_analisadas_voluntarios/
└── Exame 02-09-26 - 14-35/
    ├── Analise 01.jpg    ← bounding boxes YOLO desenhados pelo result.plot()
    ├── Analise 02.jpg
    └── detections.json
```

### Formato de `detections.json`

```json
{
  "Analise 01.jpg": [
    { "label": "normal",   "conf": 0.9321 },
    { "label": "anomalia", "conf": 0.1234 }
  ],
  "Analise 02.jpg": [],
  "Analise 03.jpg": [
    { "label": "normal", "conf": 0.8754 }
  ]
}
```

- `label`: classe detectada (definida no modelo YOLO treinado)
- `conf`: confiança 0.0–1.0
- `[]`: nenhuma detecção nessa imagem

---

## 10. Dependências e Requisitos

### Obrigatórias

```
customtkinter    # Interface gráfica
Pillow           # Exibição de imagens na UI
```

### Opcionais (graceful degradation)

```
opencv-python    # Câmera, feed ao vivo e escrita de imagens
ultralytics      # Modelo YOLO para análise
```

Se `opencv-python` ausente → câmera desabilitada, capturas não realizadas  
Se `ultralytics` ausente → análise YOLO desabilitada, `analyze_file` retorna `[]`

```bash
pip install -r requirements_pc.txt   # desenvolvimento (PC)
pip install -r requirements_rpi.txt  # produção (Raspberry Pi)
```

---

## 11. Configurações e Personalização

### Trocar modelo YOLO
```python
# main.py
MODELO_PATH = os.path.join(_APP_DIR, "models", "seu_modelo.pt")
```

### Mudar resolução da janela
```python
# ui.py — linhas 47-48
SCREEN_WIDTH  = 1024
SCREEN_HEIGHT = 600
```

### Mudar índice da câmera
```python
# main.py
camera.start(index=0)  # 0 = webcam integrada, 1 = USB externa
```

### Mudar pastas de armazenamento
```python
# main.py
CAPTURE_FOLDER  = os.path.join(_APP_DIR, "minha_pasta_capturas")
ANALYZED_FOLDER = os.path.join(_APP_DIR, "minha_pasta_analises")
```

### Mudar cores da UI
```python
# ui.py — dicionário C
C = {
    "green": "#00e676",   # destaque principal
    "amber": "#ffc107",   # cor da análise YOLO
    # ...
}
```

---

## 12. Navegação pelo Teclado / HID ESP32

O equipamento usa um ESP32 que emula um HID de teclado com teclas de seta + ENTER.

| Tecla | Função global |
|---|---|
| `↑` `↓` | Navegar opções / ajustar valores |
| `←` `→` | Selecionar botões / voltar |
| `ENTER` | Confirmar / avançar |
| `F11` | Alternar fullscreen |
| `ESC` | Sair do fullscreen ou fechar app |

### Mapeamento por tela

| Tela | ↑ | ↓ | ← | → | ENTER |
|---|---|---|---|---|---|
| T0 | — | — | — | — | → T1 |
| T1 | Sel. INICIAR | Sel. GALERIA | — | — | Confirma |
| T2 | +1 valor | −1 valor | Volta / → T1 | — | Próximo passo / → T3 |
| T3 | — | — | Sel. VOLTAR | Sel. INICIAR | Confirma |
| T4 | 🔒 | 🔒 | 🔒 | 🔒 | 🔒 |
| T4b | 🔒 | 🔒 | 🔒 | 🔒 | 🔒 |
| T5 | — | — | Sel. NOVO EXAME | Sel. GALERIA | Confirma |
| Galeria L1 | Sobe lista | Desce lista | Volta (T1/T5) | — | Abre exame |
| Galeria L2 | Sobe lista | Desce lista | → L1 | — | Abre imagem |
| Galeria L3 | Img anterior | Próxima img | → L2 | — | — |

---

*Documentação gerada automaticamente em 02/09/2026 — VisualDetect v1.0*
