import cv2
import numpy as np
import os
from ultralytics import YOLO
from pytorch_grad_cam import EigenCAM
from pytorch_grad_cam.utils.image import show_cam_on_image

# ===== CONFIGURAÇÃO =====
MODELO_PATH = "YOLOv8m_Fenecit2.pt"  # Seu modelo treinado
PASTA_ENTRADA = "fotos_teste"       # Pasta com suas fotos (voluntários/sobrevivente)
PASTA_SAIDA = "resultados_gradcam"

os.makedirs(PASTA_SAIDA, exist_ok=True)

# 1. Carregar Modelo
modelo = YOLO(MODELO_PATH)
# Escolhemos a penúltima camada da rede para ver a tomada de decisão
target_layers = [modelo.model.model[-2]]
cam = EigenCAM(modelo.model, target_layers)

print(f"Iniciando Grad-CAM em: {PASTA_ENTRADA}")

# 2. Processar Imagens
for nome_arq in os.listdir(PASTA_ENTRADA):
    if nome_arq.lower().endswith(('.png', '.jpg', '.jpeg')):
        caminho_img = os.path.join(PASTA_ENTRADA, nome_arq)
        
        # Preparar Imagem
        img = cv2.imread(caminho_img)
        img_resized = cv2.resize(img, (640, 640))
        rgb_img = img_resized[:, :, ::-1] / 255.0 # Normalização

        # Gerar Mapa de Calor
        grayscale_cam = cam(input_tensor=img_resized)[0, :]
        
        # Rodar predição para pegar a Label
        results = modelo(img_resized, conf=0.5, verbose=False)[0]
        
        # Fundir Mapa de Calor com a Imagem Original
        cam_image = show_cam_on_image(rgb_img, grayscale_cam, use_rgb=True)
        cam_image = cv2.cvtColor(cam_image, cv2.COLOR_RGB2BGR)

        # Adicionar Texto de Identificação
        if len(results.boxes) > 0:
            label = modelo.names[int(results.boxes[0].cls[0])].upper()
            conf = float(results.boxes[0].conf[0])
            texto = f"{label} ({conf*100:.1f}%)"
            cor = (0, 255, 0) if "normal" in label.lower() else (0, 165, 255)
        else:
            texto = "SEM DETECCAO"
            cor = (0, 0, 255)

        cv2.putText(cam_image, texto, (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.7, cor, 2)

        # Salvar Resultado
        cv2.imwrite(os.path.join(PASTA_SAIDA, f"gradcam_{nome_arq}"), cam_image)
        print(f" Gerado: gradcam_{nome_arq}")

print(f"\nConcluído! Veja os resultados em: {PASTA_SAIDA}")