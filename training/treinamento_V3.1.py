from ultralytics import YOLO
import torch

# ===== CONFIGURAÇÃO PARA DATASET SINTÉTICO (5K) =====
train_name = "Treino_5k__Dropout025_m"
dataset_yaml = "data.yaml"  #apontar para a pasta das 5.000 imagens

# Começar do ZERO (Importante para não trazer vícios)
base_model = "yolov8m.pt"

device = 0
batch_size = 16 
workers = 8
epochs = 200    # 200 épocas é suficiente para 5.000 imagens (muito volume)
patience = 40   # Se parar de melhorar, encerra

if __name__ == '__main__':
    
    print(f"🚀 Iniciando Treino com 5.000 Imagens + Dropout 25%...")
    print("🎯 Estratégia: Augmentation Suave (pois o dataset já é mexido) + Dropout Anti-Vício")

    model = YOLO(base_model)

    results = model.train(
        data=dataset_yaml,
        epochs=epochs,
        imgsz=640,
        batch=batch_size,
        device=device,
        name=train_name,
        workers=workers,
        patience=patience,

        # --- OTIMIZAÇÃO ---
        optimizer='AdamW',
        cos_lr=True,
        close_mosaic=10, 

        # --- DROPOUT ---
        # 0.25 (25%) é o valor de ouro para dados sintéticos.
        # Obriga a IA a ignorar 1/4 dos detalhes a cada passada,
        # impedindo ela de "decorar" as variações artificiais.
        dropout=0.25,       

        # --- AUGMENTATION (SUAVE) ---
        # ATENÇÃO: Aqui fomos mais gentis que no treino de 300 imagens.
        # Motivo: 5k imagens JÁ TÊM rotação e zoom aplicados.
        augment=True,
        
        # Cores (TRAVADAS - Segurança Médica)
        hsv_h=0.01,    # Quase zero alteração de cor
        hsv_s=0.1,     
        hsv_v=0.2,     

        # Geometria (LEVE - Para não estragar o dataset)
        degrees=5.0,   # Só 5 graus (o dataset já tem rotações maiores)
        translate=0.1, 
        scale=0.2,     # Zoom leve (20%)
        shear=0.0,     
        perspective=0.0,

        # Mix (Ajuda a generalizar)
        mosaic=1.0,
        mixup=0.1,    
        copy_paste=0.0,
    )

    print("✅ TREINO 5K FINALIZADO!")