# VisualDetect - Retinoblastoma Detection using YOLO

Projeto de detecção de Retinoblastoma usando YOLO (You Only Look Once) com YOLOv8.

## Descrição

VisualDetect é um sistema de visão computacional que utiliza redes neurais YOLOv8 para detectar sintomas de Retinoblastoma em imagens de olhos.

## Estrutura do Projeto

```
VisualDetect/
├── Main/                 # Aplicação principal
│   ├── detection.py     # Script de detecção em webcam
│   ├── batch_processor.py
│   ├── capture_webcam.py
│   ├── GC9A01_simu.py   # Simulação de tela
│   ├── videos/
│   └── capturas/
├── augment_yolo.py      # Augmentação de dados
├── name_ organizes.py
└── requirements.txt
```

## Instalação

1. Clone o repositório
2. Crie um ambiente virtual:
```bash
python -m venv .venv
.venv\Scripts\Activate.ps1  # No Windows
source .venv/bin/activate   # No Linux/Mac
```

3. Instale as dependências:
```bash
pip install -r requirements.txt
```

## Dependências

- **ultralytics** - Framework YOLO
- **opencv-python** - Processamento de imagem
- **torch/torchvision** - Deep Learning
- **Pillow** - Manipulação de imagens
- **luma.core/luma.emulator** - Display emulation
- **pygame** - Renderização

## Uso

### Detecção em Webcam
```bash
python Main/detection.py
```

### Processamento em Lote
```bash
python Main/batch_processor.py
```

### Captura de Webcam
```bash
python Main/capture_webcam.py
```

## Nota Importante

Os arquivos de treinamento (`trainings/`) e o dataset não estão inclusos no repositório. Para utilizar o projeto:
- Coloque os modelos pré-treinados em `trainings/runs/detect/`
- Atualize os caminhos em `detection.py` conforme necessário

## Licença

Este projeto é de uso interno.
