# VisualDetect — Detecção de Retinoblastoma com YOLO

Sistema de visão computacional para detecção de **Retinoblastoma** (reflexo pupilar anormal) utilizando modelos YOLOv8/YOLO11, com interface gráfica dedicada para uso no Raspberry Pi 4.

---

## Estrutura do Projeto

```
VisualDetect/
│
├── app/                                     # Pasta autocontida — deploy no Raspberry Pi
│   ├── main.py                              # Ponto de entrada (inicializa backend + UI)
│   ├── backend.py                           # Lógica: CameraManager, VisionAnalyzer, CaptureSession
│   ├── ui.py                                # Interface gráfica customtkinter (telas T0–T5)
│   ├── assets/                              # Logos e imagens da interface
│   ├── models/                              # Modelo YOLO treinado (não versionado)
│   │   └── best.pt                          # ← coloque aqui com este nome exato
│   ├── capturas_voluntarios_analisar/       # Fotos brutas do exame (criada ao rodar)
│   └── capturas_analisadas_voluntarios/     # Fotos anotadas pelo YOLO (criada ao rodar)
│
├── docs/                                    # Toda a documentação do projeto
│   ├── user_guide/
│   │   └── GUIA_DO_USUARIO.md              # Para o médico / usuário final
│   ├── dev/
│   │   ├── INSTALL_PC.md                   # Rodar no Windows (desenvolvedor)
│   │   ├── INSTALL_RASPBERRY.md            # Instalar no Raspberry Pi (técnico)
│   │   ├── install_rpi.sh                  # Script de instalação automatizada
│   │   └── visualdetect.service            # Unidade systemd para autostart
│   └── interface/                          # Mockups e assets de design
│       ├── Icons_logos/
│       └── Concepts/
│
├── firmware/                                # Firmware embarcado (ESP32)
│   ├── esp32_hid_controller/
│   │   └── esp32_hid_controller.ino        # Controlador HID USB (teclado físico)
│   ├── tft_display_154/                    # Firmware display TFT (ST7789)
│   └── README.md                           # Pinagem, dependências e integração
│
├── analysis/                               # Análise e validação de modelos
│   ├── validacao_cruzada_10fold_final.py
│   └── ...
│
├── training/                               # Treinamento YOLO
│   ├── treinamento_V3.1.py
│   ├── data.yaml
│   └── ...
│
├── capture/                                # Scripts legados de captura (sem UI)
├── scripts/                                # Utilitários de dados
│
├── requirements_pc.txt                     # Dependências Python para PC (desenvolvimento)
├── requirements_rpi.txt                    # Dependências extras do Raspberry Pi
└── .gitignore
```

> **Nota:** As pastas `app/models/`, `app/capturas_*/`, `training/datasets/`, `data/` e `runs/` não são versionadas (ver `.gitignore`).

---

## Documentação

| Documento | Público-alvo | Link |
|-----------|-------------|------|
| Este README | Desenvolvedores | — |
| Guia do Usuário | Médico / usuário final | [GUIA_DO_USUARIO.md](docs/user_guide/GUIA_DO_USUARIO.md) |
| Instalação no PC | Desenvolvedor | [INSTALL_PC.md](docs/dev/INSTALL_PC.md) |
| Instalação no Raspberry Pi | Técnico / desenvolvedor | [INSTALL_RASPBERRY.md](docs/dev/INSTALL_RASPBERRY.md) |
| Firmware ESP32 | Desenvolvedor de hardware | [firmware/README.md](firmware/README.md) |

---

## Instalação Rápida

### PC (Windows) — Desenvolvimento

```powershell
git clone https://github.com/MYuri-beck/visual-detect.git
cd visual-detect
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements_pc.txt
```

Coloque o modelo em `app/models/best.pt` e rode:

```powershell
.venv\Scripts\python.exe app\main.py
```

### Raspberry Pi — Deploy

```bash
git clone https://github.com/MYuri-beck/visual-detect.git VisualDetect
cd VisualDetect
bash docs/dev/install_rpi.sh
```

> Guia completo: [`docs/dev/INSTALL_RASPBERRY.md`](docs/dev/INSTALL_RASPBERRY.md)

---

## Uso da Aplicação

```bash
# Janela 800×480 (desenvolvimento / PC)
python app/main.py

# Tela cheia (Raspberry Pi 4 com display)
python app/main.py --fullscreen
```

---

## Interface Gráfica — Fluxo de Telas

Interface otimizada para display **800×480** e navegação via teclado/ESP32 HID:

| Tela | Descrição |
|------|-----------|
| **Loading** | Carrega o modelo YOLO em background |
| **T0** | Informações SENAI / NUDEP |
| **T1** | Splash VisualDetect |
| **T2** | Configuração do exame (modo wizard) |
| **T3** | Revisão + feed ao vivo da câmera |
| **T4** | Capturando (automático, botões bloqueados) |
| **T5** | Exame concluído |

| Tecla | Ação |
|-------|------|
| `←` / `→` | Selecionar / voltar |
| `↑` / `↓` | Ajustar valor |
| `Enter` | Confirmar / avançar |
| `F11` | Fullscreen |
| `Esc` | Sair |

---

## Controle Físico — ESP32 HID

O ESP32-S2/S3 é conectado via USB ao Raspberry Pi e se registra como **teclado HID**.

```
Botões físicos → ESP32-S2/S3 (USB HID) → Raspberry Pi 4 → app/main.py
```

| Pino ESP32 | Função |
|------------|--------|
| 5 | Seta Direita |
| 6 | Seta Esquerda |
| 7 | Seta Cima |
| 8 | Seta Baixo |
| 9 | Enter |

Consulte [`firmware/README.md`](firmware/README.md) para instruções de gravação.

---

## Dependências Principais

| Pacote | Uso |
|--------|-----|
| `ultralytics` | Framework YOLO (treino e inferência) |
| `opencv-python` | Câmera e processamento de imagem |
| `torch` / `torchvision` | Deep Learning |
| `Pillow` | Feed de câmera na UI |
| `customtkinter` | Interface gráfica |
| `scikit-learn` | Validação cruzada e métricas |
| `picamera2` *(RPi, via apt)* | Câmera módulo Raspberry Pi |
| `pyserial` *(RPi)* | Comunicação USB com ESP32 |

---

## Licença

Este projeto é de uso interno / acadêmico — SENAI / NUDEP.
