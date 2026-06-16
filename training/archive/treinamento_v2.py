from ultralytics import YOLO
import torch
import os

# ===== 1. CONFIGURAÇÕES =====
# Nome do treino 
train_name = "YOLOv8m_V2_2026"

# Caminho do dataset (Certifique-se que o arquivo existe)
dataset_yaml = "data.yaml"

# Modelo Base: Começamos do ZERO com o modelo oficial.
# Isso garante que ele aprenda com suas 5000 imagens sem vícios antigos.
base_model = "yolov8m.pt"

# Hardware (Ajustado para Lenovo LOQ RTX 4050 6GB)
device = 0
batch_size = 16    
workers = 8        # Processadores trabalhando
epochs = 300       # Quantidade ideal para dataset grande
patience = 50      # Para se não evoluir mais
img_size = 640

# ===== 2. BLOCO DE EXECUÇÃO =====
if __name__ == '__main__':
    
    # Verifica GPU
    if torch.cuda.is_available():
        gpu_name = torch.cuda.get_device_name(0)
        print(f"✅ GPU Detectada e Pronta: {gpu_name}")
    else:
        print("⚠️ AVISO: GPU não encontrada! O treino será muito lento na CPU.")

    print(f"🚀 Iniciando treino BLINDADO com dataset de 5.000 imagens...")
    
    # Carrega modelo virgem
    model = YOLO(base_model)

    # ===== TREINAMENTO =====
    results = model.train(
        data=dataset_yaml,
        epochs=epochs,
        imgsz=img_size,
        batch=batch_size,
        device=device,
        name=train_name,
        workers=workers,
        patience=patience,

        # --- OTIMIZAÇÃO TÉCNICA ---
        optimizer='AdamW',   # Otimizador mais estável para esse volume de dados
        cos_lr=True,         # Refina o aprendizado no final
        close_mosaic=20,     # Foca na imagem real nas últimas 20 épocas

        # --- AUGMENTATION INTELIGENTE (Suave) ---
        # Como as imagens JÁ SÃO aumentadas, somos gentis aqui.
        augment=True,
        
        # CORES (CRÍTICO): Quase não tocamos para manter o branco/vermelho reais.
        hsv_h=0.0,    # Matiz: 0.0 (NÃO MUDAR A COR DO REFLEXO)
        hsv_s=0.1,    # Saturação: Leve variação (10%)
        hsv_v=0.1,    # Brilho: Leve variação (10%)

        # GEOMETRIA: Ajustes finos apenas
        degrees=5.0,       # Rotação pequena (+/- 5 graus)
        translate=0.05,    # Move levemente
        scale=0.2,         # Zoom leve (simula distância da câmera)
        shear=0.0,         # Zero deformação
        perspective=0.000, # Zero distorção 3D

        # TÉCNICAS EXTRAS
        fliplr=0.5,        # Espelhamento Horizontal: OK (Olho esquerdo vira direito)
        flipud=0.0,        # Espelhamento Vertical: DESLIGADO (Não existe olho invertido)
        mosaic=1.0,        # Mantemos o Mosaic (ótimo para ensinar a achar objetos pequenos)
        mixup=0.05,        # Mistura bem leve
    )

    print("\n==================================================")
    print("✅ TREINO FINALIZADO COM SUCESSO!")
    print(f"📊 Resultados salvos em: runs/detect/{train_name}")
    print("==================================================")