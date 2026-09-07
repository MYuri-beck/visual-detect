# Diagramas de Sequência — VisualDetect

> **Projeto:** VisualDetect — Equipamento de Triagem do Reflexo Ocular
> **Versão:** 1.0 · Setembro 2026
> **Autores:** Yuri Mendes | Andrei Krug

Os diagramas estão divididos em **5 partes** cobrindo todos os fluxos do sistema:

| Parte | Fluxo |
|-------|-------|
| [1](#parte-1--inicialização-do-sistema) | Inicialização do sistema (`main.py` → Loading → T0) |
| [2](#parte-2--navegação-e-configuração-do-exame) | Navegação e configuração do exame (T1 → T2 → T3) |
| [3](#parte-3--captura-de-imagens) | Captura de imagens (T3 → T4) |
| [4](#parte-4--análise-yolo-e-persistência) | Análise YOLO e persistência (T4b) |
| [5](#parte-5--galeria-e-controle-hid) | Galeria e controle físico HID (Pico 2W) |

---

## Parte 1 — Inicialização do Sistema

> Cobre o startup do processo: instanciação dos objetos de backend, carregamento assíncrono do modelo YOLO e exibição da tela de loading.

```mermaid
sequenceDiagram
    autonumber
    participant OS  as Sistema Operacional
    participant MP  as main.py
    participant CM  as CameraManager
    participant VA  as VisionAnalyzer
    participant CS  as CaptureSession
    participant UI  as VisualDetectUI
    participant SL  as ScreenLoading

    OS->>MP: python main.py [--fullscreen]
    MP->>CM: CameraManager()
    MP->>CM: camera.start(index=1)
    CM-->>CM: Thread _loop() [daemon, ~30 FPS]
    CM-->>MP: True (câmera aberta)

    MP->>VA: VisionAnalyzer(model_path)
    Note over VA: modelo ainda NÃO carregado

    MP->>CS: CaptureSession(camera, analyzer, capture_folder, analyzed_folder)
    CS-->>CS: makedirs(capture_folder, analyzed_folder)
    CS-->>MP: session

    MP->>UI: VisualDetectUI(backend_session=session)
    UI-->>UI: bind(KeyPress, Escape, F11)
    UI->>UI: show_screen("loading")
    UI->>SL: ScreenLoading(app)

    SL->>VA: analyzer.load_async(on_ready=callback)
    VA-->>VA: Thread _worker() [daemon]
    Note over SL: mostra barra indeterminada + animação de pontos

    VA-->>VA: YOLO(model_path) — carrega pesos
    VA-->>SL: on_ready() via after(0, _on_model_ready)

    SL-->>SL: progress.stop()
    SL-->>SL: label "Pronto!" (verde)
    SL->>UI: after(600ms) → show_screen("t0")
    Note over UI: ScreenT0 exibida (info SENAI/NUDEP)
```

---

## Parte 2 — Navegação e Configuração do Exame

> Cobre a jornada do usuário desde a tela inicial (T0) até a tela de revisão com feed de câmera (T3), passando pelo wizard de configuração (T2).

```mermaid
sequenceDiagram
    autonumber
    participant HID as Pico 2W (HID)
    participant UI  as VisualDetectUI
    participant T0  as ScreenT0
    participant T1  as ScreenT1
    participant T2  as ScreenT2
    participant T3  as ScreenT3
    participant CS  as CaptureSession
    participant CM  as CameraManager

    HID->>UI: tecla ENTER
    UI->>T0: handle_key(Return)
    T0->>UI: show_screen("t1")
    UI->>T1: ScreenT1(app)
    Note over T1: sel=0 (INICIAR em foco)

    HID->>UI: tecla Up / Down
    UI->>T1: handle_key(Up/Down)
    T1-->>T1: sel alterna entre INICIAR(0) e GALERIA(1)

    HID->>UI: tecla ENTER (INICIAR selecionado)
    UI->>T1: handle_key(Return)
    T1->>UI: show_screen("t2")
    UI->>T2: ScreenT2(app)
    Note over T2: Wizard Passo 0 — "Nr DE CAPTURAS", padrão: 10

    loop Passo 0 — ajuste de capturas
        HID->>UI: tecla Up / Down
        UI->>T2: handle_key(Up/Down)
        T2->>CS: session.image_number += delta
        T2-->>T2: _refresh() — flash verde no valor
    end

    HID->>UI: tecla ENTER
    UI->>T2: handle_key(Return)
    T2-->>T2: step=1 — "TEMPO TOTAL", padrão: 10s

    loop Passo 1 — ajuste de tempo
        HID->>UI: tecla Up / Down
        UI->>T2: handle_key(Up/Down)
        T2->>CS: session.total_time += delta
        T2-->>T2: _refresh()
    end

    HID->>UI: tecla ENTER (último passo)
    UI->>T2: handle_key(Return)
    T2->>UI: show_screen("t3")
    UI->>T3: ScreenT3(app)

    T3->>CM: camera.available?
    alt câmera parada (vinda de exame anterior)
        CM-->>T3: False
        T3->>CM: camera.start()
    end
    T3-->>T3: _update_feed() — loop a cada 50ms
    Note over T3: Exibe resumo (capturas, tempo, intervalo) + feed ao vivo

    HID->>UI: tecla Left / Right
    UI->>T3: handle_key(Left/Right)
    T3-->>T3: sel alterna entre VOLTAR(0) e INICIAR(1)
```

---

## Parte 3 — Captura de Imagens

> Cobre o fluxo de captura automática periódica (T3 → T4), incluindo as threads paralelas de captura e de atualização da UI.

```mermaid
sequenceDiagram
    autonumber
    participant HID as Pico 2W (HID)
    participant UI  as VisualDetectUI
    participant T3  as ScreenT3
    participant T4  as ScreenT4
    participant CS  as CaptureSession
    participant CM  as CameraManager
    participant FS  as Sistema de Arquivos

    HID->>UI: tecla ENTER (INICIAR selecionado)
    UI->>T3: handle_key(Return)
    T3->>UI: app.start_exam()
    UI->>UI: show_screen("t4")
    UI->>T4: ScreenT4(app)
    UI->>T4: start_capture()

    T4->>T4: _start = time.time()
    T4->>T4: _pulse() — pisca ponto vermelho a cada 500ms
    T4->>T4: _tick() — atualiza barras de progresso a cada 50ms

    T4->>CS: session.start_exam(on_progress_callback, on_capture_done_callback)
    CS-->>CS: session_ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    CS-->>CS: Thread _capture_loop() [daemon]

    Note over CS,CM: interval = total_time / image_number

    loop Para cada captura i = 1..N
        CS->>CS: aguarda interval segundos
        CS->>CM: camera.get_frame()
        CM-->>CS: frame (BGR numpy array, espelhado)
        CS->>FS: cv2.imwrite(CAPTURE_FOLDER/ts_capture_i.jpg, frame)
        CS-->>CS: captured_images.append((fpath, fname))
        CS->>T4: on_progress_callback(i, N)
        T4-->>T4: after(0) → _sync_progress(i, N)
        T4-->>T4: atualiza barra de capturas + contador
    end

    Note over CS: Captura concluída
    CS->>T4: on_capture_done_callback(captured_images)
    T4->>T4: after(0) → _go_to_t4b()
    T4->>T4: _active = False
    T4->>UI: show_screen("t4b")
```

---

## Parte 4 — Análise YOLO e Persistência

> Cobre o processamento pós-captura: análise com YOLO em background (T4b), persistência dos resultados e navegação para a tela de conclusão (T5).

```mermaid
sequenceDiagram
    autonumber
    participant UI  as VisualDetectUI
    participant T4b as ScreenT4b
    participant CS  as CaptureSession
    participant VA  as VisionAnalyzer
    participant CM  as CameraManager
    participant FS  as Sistema de Arquivos
    participant T5  as ScreenT5

    UI->>T4b: ScreenT4b(app)
    T4b->>CM: camera.stop()
    Note over CM: libera CPU para análise YOLO

    T4b-->>CS: session._ui_analyze_progress_cb = _on_progress_thread
    T4b-->>CS: session._ui_analyze_finish_cb = _on_finish (via after)
    T4b->>T4b: _animate() — spinner âmbar a cada 150ms

    Note over CS: Thread _capture_loop aguarda 400ms<br/>e inicia _analyze_all()
    CS->>CS: _analyze_all()
    CS->>FS: makedirs(ANALYZED_FOLDER / "Exame DD-MM-YY - HH-MM")

    loop Para cada imagem i = 1..N
        CS->>VA: analyzer.analyze_file(fpath, out_path)
        VA->>VA: YOLO.predict(image_path, device="cpu")
        VA->>FS: cv2.imwrite(out_path, result.plot())
        VA-->>CS: [(label, confiança), ...]
        CS-->>CS: detections_map[out_name] = [{label, conf}, ...]
        CS->>T4b: _ui_analyze_progress_cb(i, N, fname)
        T4b-->>T4b: after(0) → _sync_progress(i, N, fname)
        T4b-->>T4b: atualiza barra + porcentagem + nome do arquivo
    end

    CS->>FS: json.dump(detections_map) → detections.json
    Note over FS: Estrutura gerada por exame:<br/>capturas_analisadas_voluntarios/<br/>  Exame DD-MM-YY - HH-MM/<br/>    Analise 01.jpg … Analise N.jpg<br/>    detections.json

    CS->>T4b: _ui_analyze_finish_cb(captured_images)
    T4b->>T4b: after(0) → _on_finish()
    T4b-->>T4b: _active = False
    T4b-->>T4b: spinner "v" verde, barra 100%, "Análise concluída!"
    T4b->>UI: after(1200ms) → show_screen("t5")
    UI->>T5: ScreenT5(app)
    Note over T5: Exibe contagem de imagens e pasta do exame<br/>Opções: NOVO EXAME / VER GALERIA
```

---

## Parte 5 — Galeria e Controle Físico HID

### 5a — Navegação na Galeria

```mermaid
sequenceDiagram
    autonumber
    participant HID as Pico 2W (HID)
    participant UI  as VisualDetectUI
    participant T5  as ScreenT5
    participant GAL as ScreenGaleria
    participant CS  as CaptureSession
    participant FS  as Sistema de Arquivos

    HID->>UI: tecla Right (VER GALERIA selecionado)
    UI->>T5: handle_key(Right)
    T5-->>T5: sel=1 — destaca VER GALERIA

    HID->>UI: tecla ENTER
    UI->>T5: handle_key(Return)
    T5->>UI: app._gallery_origin = "t5"; show_screen("galeria")
    UI->>GAL: ScreenGaleria(app)

    GAL->>CS: session.get_exam_gallery()
    CS->>FS: listdir(ANALYZED_FOLDER) — ordena desc
    FS-->>CS: pastas "Exame ..."
    CS->>FS: open(detections.json) por pasta
    FS-->>CS: detections dict
    CS-->>GAL: [{name, folder, images, detections}, ...]
    Note over GAL: Nível 1 — lista de exames

    loop Nível 1 — seleciona exame
        HID->>UI: tecla Up / Down
        UI->>GAL: handle_key(Up/Down)
        GAL-->>GAL: exam_idx ±1 — destaque na lista
    end

    HID->>UI: tecla ENTER
    UI->>GAL: handle_key(Return)
    GAL-->>GAL: level=2 → _show_level2()
    Note over GAL: Nível 2 — lista "Analise NN.jpg"

    loop Nível 2 — seleciona imagem
        HID->>UI: tecla Up / Down
        UI->>GAL: handle_key(Up/Down)
        GAL-->>GAL: image_idx ±1
    end

    HID->>UI: tecla ENTER
    UI->>GAL: handle_key(Return)
    GAL-->>GAL: level=3 → _show_level3()
    Note over GAL: Nível 3 — imagem anotada + detecções + confiança %

    HID->>UI: tecla Left
    UI->>GAL: handle_key(Left)
    GAL-->>GAL: level=2 → _show_level2()

    HID->>UI: tecla Left
    UI->>GAL: handle_key(Left)
    GAL-->>GAL: level=1 → _show_level1()

    HID->>UI: tecla Left (sair da galeria)
    UI->>GAL: handle_key(Left)
    GAL->>UI: show_screen(gallery_origin)
    Note over UI: Volta para T1 (acesso direto) ou T5 (pós-exame)
```

### 5b — Ciclo de Controle HID (Pico 2W)

```mermaid
sequenceDiagram
    autonumber
    participant BTN as Botão Físico (GPIO)
    participant PW  as Pico 2W (RP2350)
    participant USB as USB HID
    participant RPI as Raspberry Pi 4
    participant UI  as VisualDetectUI

    Note over PW: setup() — INPUT_PULLUP em GPIOs 5-9<br/>Keyboard.begin()

    loop loop() — a cada 5ms
        PW->>BTN: digitalRead(GPIO_N)
        alt Borda de descida HIGH→LOW com debounce >= 30ms
            PW->>USB: Keyboard.press(KEY_X)
            PW->>PW: delay(15ms)
            PW->>USB: Keyboard.release(KEY_X)
        end
    end

    USB->>RPI: evento HID
    RPI->>UI: KeyPress event (tkinter binding)
    UI->>UI: _on_key(event)
    UI->>UI: current_screen.handle_key(event)
    Note over UI: Tela atual processa a tecla<br/>conforme seu contexto

    Note over BTN,UI: GPIO 5→Right, GPIO 6→Left<br/>GPIO 7→Up, GPIO 8→Down, GPIO 9→Return
```

---

## Resumo dos Participantes

| Participante | Arquivo / Hardware | Responsabilidade |
|---|---|---|
| `main.py` | `app/main.py` | Ponto de entrada — instancia e conecta todas as camadas |
| `CameraManager` | `app/backend.py` | Thread de captura contínua (~30 FPS) |
| `VisionAnalyzer` | `app/backend.py` | Carregamento e inferência YOLO |
| `CaptureSession` | `app/backend.py` | Coordena fluxo completo de um exame |
| `VisualDetectUI` | `app/ui.py` | Janela principal, roteamento de telas e teclado |
| `ScreenLoading` | `app/ui.py` | Tela de loading do modelo YOLO |
| `ScreenT0–T5` | `app/ui.py` | Telas individuais da aplicação |
| `ScreenGaleria` | `app/ui.py` | Biblioteca de exames analisados (3 níveis) |
| `Pico 2W (RP2350)` | `firmware/.../pico2w_hid_controller.ino` | Controle físico via USB HID |
| `Sistema de Arquivos` | Disco local | Persistência de imagens e `detections.json` |
