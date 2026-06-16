from ultralytics import YOLO
import torch

# ===== CONFIGURAÇÕES 3 (VIABILIDADE) =====
dataset_yaml = "data.yaml" 

# Começamos do zero para limpar vícios anteriores
base_model = "yolov8m.pt"

# Hardware (Lenovo RTX 4050)
device = 0
batch_size = 16 
img_size = 640
train_name = "treino_300_dropout_m"
workers = 8
epochs = 300 
patience = 75 

if __name__ == '__main__':
    
    print(f"🚀 Iniciando Treino de Viabilidade (Dataset Original)...")
    print("🎯 Foco: Maximizar acerto nas 300 imagens disponíveis.")

    model = YOLO(base_model)

    train_results = model.train(
        data=dataset_yaml,
        epochs=epochs,
        imgsz=img_size,
        batch=batch_size,
        device=device,
        name=train_name,
        workers=workers,
        patience=patience,

        # ---- OTIMIZAÇÃO PARA DATASET PEQUENO ----
        optimizer='AdamW',
        cos_lr=True,
        close_mosaic=20,
        
        # DROPOUT ALTO (0.3): 
        # Como temos poucas imagens, desligamos 30% dos neurônios a cada rodada.
        # Isso impede a IA de "decorar" pixels específicos.
        dropout=0.3,       

        # ---- AUGMENTATION (AGRESSIVO NA GEOMETRIA) ----
        augment=True,
        
        # Cores: Mantemos travadas. A cor Branca é sagrada para o diagnóstico.
        hsv_h=0.01,    # Quase zero mudança de cor
        hsv_s=0.1,     
        hsv_v=0.2,     # Aceita variações de luz (sombra/claridade)

        
        # Vamos girar e dar zoom com força para simular variedade que não temos.
        degrees=25.0,  # Rotação forte (cabeça torta)
        translate=0.1, 
        scale=0.7,     # Zoom muito forte (0.7). Simula câmera bem perto e bem longe.
        shear=0.0,     # Não deformar a pupila (tem que ser redonda)
        perspective=0.0005,

        # Espelhamento (Dobra o dataset de graça)
        fliplr=0.5,    
        flipud=0.0,    

        # Mix (Ajuda a criar cenários novos misturando as fotos)
        mosaic=1.0,
        mixup=0.2,     
        copy_paste=0.0,
    )

    print("✅ TREINO DE VIABILIDADE FINALIZADO!")