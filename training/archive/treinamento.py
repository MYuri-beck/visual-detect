from ultralytics import YOLO
import os

# ===== CONFIGURAÇÕES (Podem ficar fora) =====
dataset_yaml = "data.yaml"

# Vamos usar o caminho relativo que consertamos antes
base_model = "runs/detect/treio_yolov8m_fenecit/weights/best.pt"

epochs = 350
batch_size = 16 
img_size = 640
device = 0
train_name = "treino_YOLO8m_2026"
workers = 8
patience = 50


if __name__ == '__main__':
    # Tudo que executa ação deve ficar indentado aqui dentro
    
    print(f"🚀 Iniciando treino na GPU: {device} com Batch {batch_size}...")

    # Carregar modelo
    # Verificação de segurança para o caminho
    if not os.path.exists(base_model):
        print(f"⚠️ AVISO: Não achei o modelo em '{base_model}'.")
        print("Tentando baixar o yolov8m.pt oficial para começar do zero...")
        base_model = "yolov8m.pt"
    
    model = YOLO(base_model)

    # ===== TREINAMENTO =====
    train_results = model.train(
        data=dataset_yaml,
        epochs=epochs,
        imgsz=img_size,
        batch=batch_size,
        device=device,
        name=train_name,
        workers=workers,
        patience=patience,

        # ---- CONFIGURAÇÕES DE OTIMIZAÇÃO ----
        optimizer='AdamW',
        cos_lr=True,
        close_mosaic=20,

        # ---- AUGMENTAÇÕES MÉDICAS ----
        augment=True,
        hsv_h=0.015,
        hsv_s=0.3,
        hsv_v=0.3,
        degrees=10.0,
        translate=0.1,
        scale=0.5,
        shear=0.0,
        perspective=0.0001,
        mosaic=1.0,
        mixup=0.1,
        copy_paste=0.0,
    )

    print("✅ Treino finalizado com sucesso!")
    print(f"📦 Pesos salvos em: runs/detect/{train_name}/weights/best.pt")