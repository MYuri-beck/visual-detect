import cv2
import numpy as np
import os
from ultralytics import YOLO
from pytorch_grad_cam import GradCAM
from pytorch_grad_cam.utils.image import show_cam_on_image
from pathlib import Path
import torch

# ===== CONFIGURAÇÃO =====
PASTA_MODELOS = "C:\\Users\\yurim\\Desktop\\Software Visual Detect\\VisualDetect\\trainings\\runs\\detect"  # Pasta com subpastas contendo best.pt
PASTA_IMAGENS = "capturas_voluntarios_analisar"  # Pasta com as fotos dos voluntários
PASTA_RAIZ_SAIDA = "GRAD_CAM_VOLUNTARIOS"

os.makedirs(PASTA_RAIZ_SAIDA, exist_ok=True)

# 1. Especificar o modelo fenecit2 diretamente
modelos_arquivos = [os.path.join(PASTA_MODELOS, "treio_yolov8m_fenecit2", "weights", "best.pt")]

if not modelos_arquivos:
    print(f" Nenhum arquivo best.pt encontrado em {PASTA_MODELOS}")
    exit()

print(f" Encontrados {len(modelos_arquivos)} modelos (best.pt) para análise:")
for modelo_path in modelos_arquivos:
    # Pegar o nome da pasta do experimento (avô do best.pt)
    modelo_dir = os.path.dirname(modelo_path)  # pasta weights
    experimento_dir = os.path.dirname(modelo_dir)  # pasta do experimento
    nome_experimento = os.path.basename(experimento_dir)
    print(f"  - {nome_experimento} (path: {modelo_path})")

# 2. Loop Principal: Percorrer cada modelo
for caminho_modelo in modelos_arquivos:
    # Pegar o nome da pasta do experimento (avô do best.pt)
    modelo_dir = os.path.dirname(caminho_modelo)  # pasta weights
    experimento_dir = os.path.dirname(modelo_dir)  # pasta do experimento
    nome_puro_modelo = os.path.basename(experimento_dir)  # nome do experimento
    
    print(f"\nProcessando com o modelo: {nome_puro_modelo}...")
    
    # Criar pasta específica para este modelo
    pasta_saida_modelo = os.path.join(PASTA_RAIZ_SAIDA, f"{nome_puro_modelo}")
    os.makedirs(pasta_saida_modelo, exist_ok=True)
    
    # Carregar o modelo atual
    try:
        modelo = YOLO(caminho_modelo)
        device = 'cuda' if torch.cuda.is_available() else 'cpu'
        modelo.model.to(device)
        target_layers = [modelo.model.model[-3]]
        cam = GradCAM(modelo.model, target_layers)
    except Exception as e:
        print(f" Erro ao carregar {nome_puro_modelo}: {e}")
        continue

    # 3. Loop Secundário: Processar as imagens para este modelo
    for nome_img in os.listdir(PASTA_IMAGENS):
        if nome_img.lower().endswith(('.png', '.jpg', '.jpeg')):
            caminho_img = os.path.join(PASTA_IMAGENS, nome_img)
            
            # Extrair ID da imagem (assumindo formato como "1_owr_lech_191123_gwalsh_jpg.rf.15f4be7221a3cc4cec7f3d84533f81c9.txt" ou similar)
            # Vamos usar o nome completo como ID
            id_imagem = Path(nome_img).stem  # Remove extensão
            
            # Carregar e redimensionar
            img = cv2.imread(caminho_img)
            if img is None: 
                print(f"  ⚠️  Erro ao carregar {nome_img}")
                continue
            
            img_resized = cv2.resize(img, (640, 640))
            # Converter BGR -> RGB e normalizar para 0-1
            img_rgb = cv2.cvtColor(img_resized, cv2.COLOR_BGR2RGB).astype(np.float32) / 255.0
            rgb_img = img_rgb

            # Gerar Grad-CAM
            try:
                # Converter para tensor PyTorch: (H, W, C) -> (1, C, H, W)
                img_tensor = torch.from_numpy(img_rgb).permute(2, 0, 1).unsqueeze(0)
                device = 'cuda' if torch.cuda.is_available() else 'cpu'
                img_tensor = img_tensor.to(device)
                
                # Gerar o mapa de calor
                cam_result = cam(input_tensor=img_tensor)
                # GradCAM retorna lista de arrays
                grayscale_cam = cam_result[0]
            except Exception as e:
                print(f"  ⚠️  Erro no Grad-CAM para {nome_img}: {str(e)[:100]}")
                continue
            
            # Rodar Inferência
            try:
                results = modelo(img_resized, conf=0.5, verbose=False)[0]
            except Exception as e:
                print(f"  ⚠️  Erro na inferência para {nome_img}: {e}")
                continue
            
            # Fundir Mapa de Calor
            cam_image = show_cam_on_image(rgb_img, grayscale_cam, use_rgb=True)
            cam_image = cv2.cvtColor(cam_image, cv2.COLOR_RGB2BGR)

            # Determinar resultado da classificação
            if len(results.boxes) > 0:
                label = modelo.names[int(results.boxes[0].cls[0])].upper()
                conf = float(results.boxes[0].conf[0])
                resultado = label.lower()  # "reflexo-alterado" ou "reflexo-normal"
                info = f"{label} ({conf*100:.1f}%)"
                cor = (0, 255, 0) if "normal" in label.lower() else (0, 165, 255)
            else:
                resultado = "sem_deteccao"
                info = "SEM DETECCAO"
                cor = (0, 0, 255)

            # Escreve o nome do modelo e o resultado na imagem
            cv2.putText(cam_image, f"Mod: {nome_puro_modelo}", (20, 30), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            cv2.putText(cam_image, info, (20, 60), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, cor, 2)

            # Salvar: [MODELO]_[RESULTADO]_[ID].jpg
            nome_final_arq = f"{nome_puro_modelo}_{resultado}_{id_imagem}.jpg"
            caminho_saida = os.path.join(pasta_saida_modelo, nome_final_arq)
            cv2.imwrite(caminho_saida, cam_image)
            print(f"  ✅ Salvo: {nome_final_arq}")

print(f"\n PROCESSO CONCLUÍDO!")
print(f" Verifique a pasta '{PASTA_RAIZ_SAIDA}' para ver as análises Grad-CAM.")
print(f" Cada arquivo segue o formato: modelo_resultado_id.jpg")