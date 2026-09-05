# VisualDetect — Detecção de Retinoblastoma com YOLO

> Sistema de visão computacional para triagem do **Retinoblastoma** (reflexo pupilar anormal)
> utilizando modelos YOLOv8/YOLO11, com interface gráfica dedicada para o Raspberry Pi 4.

**SENAI / NUDEP — Curso Técnico em Desenvolvimento de Sistemas — 2026**

---

## Índice

1. [O que é o VisualDetect](#o-que-é-o-visualdetect)
2. [Estrutura do Projeto](#estrutura-do-projeto)
3. [Documentação](#documentação)
4. [Instalação Rápida](#instalação-rápida)
5. [Uso da Aplicação](#uso-da-aplicação)
6. [Fluxo de Telas](#fluxo-de-telas)
7. [Controle Físico — Pico 2W HID](#controle-físico--pico-2w-hid)
8. [Dependências Principais](#dependências-principais)
9. [Licença](#licença)

---

## O que é o VisualDetect

O VisualDetect é um equipamento de triagem desenvolvido para auxiliar na detecção precoce do
Retinoblastoma — tumor ocular que afeta principalmente crianças. O sistema fotografa o olho do
paciente, analisa automaticamente o reflexo pupilar usando IA (YOLO) e apresenta o resultado
ao operador em uma interface otimizada para toque/botões físicos.

> ⚠️ O VisualDetect é uma ferramenta de **triagem**, não um diagnóstico médico.
> Qualquer resultado deve ser avaliado por um médico oftalmologista.

---

## Estrutura do Projeto

```
visual-detect/
│
├── app/                                     # Pasta autocontida — deploy no Raspberry Pi
│   ├── main.py                              # Ponto de entrada (inicializa backend + UI)
│   ├── backend.py                           # Lógica: CameraManager, VisionAnalyzer, CaptureSession
│   ├── ui.py                                # Interface gráfica customtkinter (telas T0–T5)
│   ├── assets/                              # Logos e imagens da interface
│   ├── models/
│   │   └── best.pt                          # ← Modelo YOLO treinado (não versionado)
│   ├── capturas_voluntarios_analisar/       # Fotos brutas do exame (criada ao rodar)
│   └── capturas_analisadas_voluntarios/     # Fotos anotadas pelo YOLO (criada ao rodar)
│
├── docs/
│   ├── user_guide/
│   │   └── GUIA_DO_USUARIO.md              # Para o médico / operador (linguagem acessível)
│   ├── dev/
│   │   ├── INSTALL_PC.md                   # Rodar no Windows — desenvolvedor
│   │   ├── INSTALL_RASPBERRY.md            # Instalar no Raspberry Pi — técnico
│   │   ├── install_rpi.sh                  # Script de instalação automatizada
│   │   └── visualdetect.service            # Unidade systemd para autostart
│   └── caderno_campo_*.md                  # Notas de sessão de desenvolvimento
│
├── firmware/
│   ├── pico2w_hid_controller/              # ← FIRMWARE ATIVO
│   │   ├── pico2w_hid_controller.ino       # Controlador HID (Raspberry Pi Pico 2W)
│   │   └── README.md                       # Documentação completa do firmware
│   ├── esp32_hid_controller/               # Firmware legado (ESP32-S2/S3) — referência
│   │   └── esp32_hid_controller.ino
│   ├── tft_display_154/                    # Firmware display TFT (ST7789)
│   └── README.md                           # Índice dos firmwares
│
├── analysis/                               # Análise e validação de modelos (validação cruzada)
├── training/                               # Treinamento YOLO (scripts + data.yaml)
├── capture/                                # Scripts legados de captura (sem UI)
├── scripts/                                # Utilitários de dados
│
├── requirements_pc.txt                     # Dependências Python para PC (desenvolvimento)
├── requirements_rpi.txt                    # Dependências extras do Raspberry Pi
└── .gitignore
```

> **Não versionados** (ver `.gitignore`): `app/models/`, `app/capturas_*/`,
> `training/datasets/`, `data/`, `runs/`

---

## Documentação

| Documento | Público-alvo | Link |
|---|---|---|
| Este README | Desenvolvedor | — |
| Guia do Usuário | Médico / operador | [GUIA_DO_USUARIO.md](docs/user_guide/GUIA_DO_USUARIO.md) |
| Instalação no PC | Desenvolvedor | [INSTALL_PC.md](docs/dev/INSTALL_PC.md) |
| Instalação no Raspberry Pi | Técnico / desenvolvedor | [INSTALL_RASPBERRY.md](docs/dev/INSTALL_RASPBERRY.md) |
| Firmware Pico 2W (ativo) | Dev de hardware | [firmware/pico2w_hid_controller/README.md](firmware/pico2w_hid_controller/README.md) |
| Firmware ESP32 (legado) | Dev de hardware | [firmware/README.md](firmware/README.md) |

---

## Instalação Rápida

### PC — Windows (desenvolvimento)

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

> Guia completo com troubleshooting: [`docs/dev/INSTALL_PC.md`](docs/dev/INSTALL_PC.md)

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

## Fluxo de Telas

Interface otimizada para display **800×480** e navegação via teclado / controlador HID físico:

| Tela | Nome | Descrição |
|---|---|---|
| **Loading** | Carregando | Carrega o modelo YOLO em background — avança automaticamente |
| **T0** | Info institucional | Informações SENAI / NUDEP |
| **T1** | Splash | Tela de boas-vindas + opções Iniciar / Galeria |
| **T2** | Configuração | Wizard: define nº de capturas e tempo do exame |
| **T3** | Revisão + Câmera | Feed ao vivo — posicionar paciente antes de iniciar |
| **T4** | Capturando | Fotografando automaticamente (botões bloqueados) |
| **T4b** | Analisando | YOLO processando em background (câmera parada) |
| **T5** | Concluído | Resultado + opções Novo Exame / Galeria |
| **Galeria** | Galeria | Biblioteca de exames: exame → análise → imagem |

### Teclas de navegação

| Tecla | Ação |
|---|---|
| `←` / `→` | Selecionar botão / avançar entre opções |
| `↑` / `↓` | Ajustar valor numérico (tela T2) / navegar lista (Galeria) |
| `Enter` | Confirmar seleção / avançar tela |
| `F11` | Alternar fullscreen |
| `Esc` | Sair do fullscreen / fechar |

---

## Controle Físico — Pico 2W HID

O **Raspberry Pi Pico 2W** é conectado via USB ao Raspberry Pi 4 e se registra como
**teclado USB padrão (HID)** — sem drivers adicionais necessários.

```
[ Botões físicos ] → [ Pico 2W (USB HID) ] → [ Raspberry Pi 4 ] → [ app/ui.py ]
```

| GPIO Pico 2W | Botão | Tecla HID |
|---|---|---|
| 5 | Seta Direita | `RIGHT_ARROW` |
| 6 | Seta Esquerda | `LEFT_ARROW` |
| 7 | Seta Cima | `UP_ARROW` |
| 8 | Seta Baixo | `DOWN_ARROW` |
| 9 | Confirmar | `RETURN` |

> Todos os botões ligados entre GPIO e GND (pull-up interno ativado via software).
> Consulte [`firmware/pico2w_hid_controller/README.md`](firmware/pico2w_hid_controller/README.md)
> para instruções completas de gravação e montagem.

> **Nota:** O firmware ESP32-S2/S3 original (`firmware/esp32_hid_controller/`) é mantido
> como referência histórica, mas **não é o firmware em uso**.

---

## Dependências Principais

| Pacote | Versão | Uso |
|---|---|---|
| `ultralytics` | 8.4.126 | Framework YOLO (treino e inferência) |
| `opencv-python` | 5.0.0.93 | Câmera e processamento de imagem |
| `torch` | 2.13.0 | Deep Learning (PyTorch) |
| `torchvision` | 0.28.0 | Transformações de imagem |
| `numpy` | 2.4.6 | Operações numéricas |
| `Pillow` | 12.3.0 | Feed de câmera na UI |
| `customtkinter` | 6.0.0 | Interface gráfica |
| `matplotlib` | 3.11.1 | Visualização de métricas |
| `scikit-learn` | 1.9.0 | Validação cruzada e métricas |
| `pyserial` *(RPi)* | 3.5 | Comunicação USB serial |
| `picamera2` *(RPi, via apt)* | — | Câmera módulo Raspberry Pi |

---

## Licença

Este projeto é de uso interno / acadêmico — SENAI / NUDEP.  
Desenvolvido como projeto do Curso Técnico em Desenvolvimento de Sistemas, 2026.
