# VisualDetect — Detecção de Retinoblastoma com YOLO

Sistema de visão computacional para detecção de sintomas de **Retinoblastoma** (reflexo pupilar anormal) utilizando modelos YOLOv8, com suporte a captura via webcam e processamento em lote no Raspberry Pi 4.

---

## Estrutura do Projeto

```
VisualDetect/
├── analysis/                        # Análise e validação
│   ├── 10-Fold_cross_validation.py
│   ├── validacao_cruzada_10fold_final.py
│   ├── fold_10_only.py
│   ├── analise_modelos.py
│   ├── check_cuda.py
│   └── archive/                     # Scripts antigos (referência)
│
├── capture/                         # Captura e processamento de imagens
│   ├── batch_processor.py           # Script principal (Raspberry Pi 4)
│   ├── capture_webcam.py
│   ├── detection.py
│   ├── image_processor.py
│   └── archive/                     # Versões antigas do batch_processor
│
├── firmware/                        # Firmware embarcado (ESP32)
│   ├── esp32_hid_controller/
│   │   └── esp32_hid_controller.ino # Controlador HID USB (teclado físico)
│   └── README.md                    # Pinagem, dependências e integração
│
├── training/                        # Treinamento YOLO
│   ├── treinamento_V3.1.py          # Script de treino (versão final)
│   ├── data.yaml                    # Configuração do dataset
│   ├── datasets/                    # Train/valid/test (não versionado)
│   ├── runs/                        # Resultados de treino (não versionado)
│   └── archive/                     # Versões antigas dos scripts de treino
│
├── models/                          # Modelos .pt (não versionado)
├── scripts/                         # Scripts utilitários
│   ├── augment_yolo.py              # Augmentação de dados
│   └── name_ organizes.py
│
├── data/                            # Capturas de voluntários (não versionado)
├── requirements.txt                 # Dependências core (PC + RPi4)
├── requirements_rpi.txt             # Dependências exclusivas do Raspberry Pi 4
└── .gitignore
```

> **Nota:** As pastas `models/`, `training/datasets/`, `training/runs/` e `data/` não são versionadas (ver `.gitignore`).

---

## Instalação

### 1. Clone o repositório
```bash
git clone https://github.com/MYuri-beck/visual-detect.git
cd visual-detect
```

### 2. Crie e ative um ambiente virtual
```bash
python -m venv .venv

# Windows
.venv\Scripts\Activate.ps1

# Linux / Raspberry Pi
source .venv/bin/activate
```

### 3. Instale as dependências

**PC / Windows:**
```bash
pip install -r requirements.txt
```

**Raspberry Pi 4** (instalar após o core):
```bash
pip install -r requirements.txt
pip install -r requirements_rpi.txt
```

---

## Dependências Principais

| Pacote | Uso |
|---|---|
| `ultralytics` | Framework YOLO (treino e inferência) |
| `opencv-python` | Captura de câmera e processamento de imagem |
| `torch` / `torchvision` | Deep Learning |
| `Pillow` | Manipulação de imagens |
| `scikit-learn` | Validação cruzada e métricas |
| `picamera2` *(RPi4)* | Câmera do Raspberry Pi |

---

## Uso

### Captura e detecção em lote (Raspberry Pi 4)
```bash
python capture/batch_processor.py
```

### Detecção em webcam
```bash
python capture/detection.py
```

### Captura via webcam
```bash
python capture/capture_webcam.py
```

### Validação cruzada (10-Fold)
```bash
python analysis/validacao_cruzada_10fold_final.py
```

### Treinamento
```bash
# Configurar data.yaml e caminhos em training/treinamento_V3.1.py
python training/treinamento_V3.1.py
```

---

## Controle físico — ESP32 HID

O ESP32 é conectado via USB ao Raspberry Pi 4 e se registra como **teclado HID**.
Os botões físicos enviam teclas de seta e Enter para navegar na interface do `batch_processor.py`.

Consulte [`firmware/README.md`](firmware/README.md) para esquema de pinos, dependências do Arduino IDE e instruções de gravação.

```
Botões físicos → ESP32 (USB HID) → Raspberry Pi 4 → batch_processor.py
```

---

## Nota sobre Modelos e Dados

- Os modelos treinados (`.pt`) devem ser colocados em `models/` e **não** são versionados.
- O caminho do modelo em `capture/batch_processor.py` aponta para `../training/runs/detect/<NOME_DO_TREINO>/weights/best.pt` — ajuste `NOME_DO_TREINO` conforme o treino utilizado.
- Os dados de voluntários em `data/` são mantidos localmente por questões de privacidade.

---

## Licença

Este projeto é de uso interno / acadêmico.
