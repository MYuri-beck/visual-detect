import cv2
import albumentations as A
import os
import numpy as np
import glob

# --- Configuração ---
# Nome da pasta que contém o seu dataset (train/test/valid)
NOME_PASTA_DATASET = "Reflexo vermelho.v3i.yolov11"

# Caminhos baseados na localização do script (em AUMENTA_DATASET)
PASTA_TRAIN_IMG = os.path.join(NOME_PASTA_DATASET, "train/images")
PASTA_TRAIN_LBL = os.path.join(NOME_PASTA_DATASET, "train/labels")

# Novas pastas que serão criadas DENTRO da pasta do dataset
PASTA_AUMENTADA_IMG = os.path.join(NOME_PASTA_DATASET, "train_augmented/images")
PASTA_AUMENTADA_LBL = os.path.join(NOME_PASTA_DATASET, "train_augmented/labels")

# Quantas novas versões criar para CADA imagem original
IMAGENS_POR_ORIGINAL = 14 

# --- Crie as pastas de destino se elas não existirem ---
os.makedirs(PASTA_AUMENTADA_IMG, exist_ok=True)
os.makedirs(PASTA_AUMENTADA_LBL, exist_ok=True)

# --- Defina o Pipeline de Aumentação (O mesmo da nossa conversa) ---
transform = A.Compose([
    A.Rotate(limit=15, p=0.7),
    A.RandomBrightnessContrast(brightness_limit=0.2, contrast_limit=0.2, p=0.8),
    A.HorizontalFlip(p=0.5),
    A.GaussNoise(var_limit=(10.0, 50.0), p=0.5),
    A.ShiftScaleRotate(shift_limit=0.05, scale_limit=0.1, rotate_limit=0, p=0.6),
    A.GaussianBlur(blur_limit=(3, 7), p=0.5)
], bbox_params=A.BboxParams(format='yolo', label_fields=['class_labels'], min_visibility=0.1))
# --- Funções Auxiliares para ler e salvar labels YOLO ---

def ler_yolo_labels(caminho_label):
    bboxes = []
    class_labels = []
    if not os.path.exists(caminho_label):
        return bboxes, class_labels
        
    with open(caminho_label, 'r') as f:
        for line in f.readlines():
            parts = line.strip().split()
            if len(parts) == 5:
                class_labels.append(int(parts[0]))
                bboxes.append([float(p) for p in parts[1:]])
    return bboxes, class_labels

def salvar_yolo_labels(caminho_salvar, bboxes, class_labels):
    with open(caminho_salvar, 'w') as f:
        for bbox, label in zip(bboxes, class_labels):
            # Formato: class_id x_center y_center width height
            line = f"{label} {bbox[0]} {bbox[1]} {bbox[2]} {bbox[3]}\n"
            f.write(line)

# --- Processamento das Imagens e Labels ---
def aumentar_dataset_yolo():
    print(f"Iniciando aumento de dados (YOLO - Estrutura Roboflow)...")
    print(f"Lendo imagens de: {PASTA_TRAIN_IMG}")
    print(f"Lendo labels de: {PASTA_TRAIN_LBL}")
    print(f"Salvando imagens em: {PASTA_AUMENTADA_IMG}")
    print(f"Salvando labels em: {PASTA_AUMENTADA_LBL}")

    # Encontra todas as imagens na pasta de treino
    imagens = glob.glob(os.path.join(PASTA_TRAIN_IMG, '*.jpg'))
    imagens.extend(glob.glob(os.path.join(PASTA_TRAIN_IMG, '*.png')))
    imagens.extend(glob.glob(os.path.join(PASTA_TRAIN_IMG, '*.jpeg')))
    
    if not imagens:
        print(f"ERRO: Nenhuma imagem encontrada em '{PASTA_TRAIN_IMG}'.")
        print(f"Verifique se o script está na pasta 'AUMENTA_DATASET' e se a pasta")
        print(f"'{NOME_PASTA_DATASET}/train/images' existe e contém imagens.")
        return

    contador_total = 0
    for caminho_imagem in imagens:
        nome_imagem = os.path.basename(caminho_imagem)
        nome_base = os.path.splitext(nome_imagem)[0]
        ext_imagem = os.path.splitext(nome_imagem)[1]
        
        caminho_label = os.path.join(PASTA_TRAIN_LBL, f"{nome_base}.txt")

        # 1. Ler imagem
        imagem_original = cv2.imread(caminho_imagem)
        imagem_original = cv2.cvtColor(imagem_original, cv2.COLOR_BGR2RGB)

        # 2. Ler labels
        bboxes_originais, labels_originais = ler_yolo_labels(caminho_label)

        if not bboxes_originais and os.path.exists(caminho_label):
            print(f"Aviso: Arquivo de label {caminho_label} está vazio, pulando {nome_imagem}...")
            continue
        elif not os.path.exists(caminho_label):
             print(f"Aviso: Nenhuma label encontrada para {nome_imagem} (arquivo .txt não existe), pulando...")
             continue

        # print(f"Processando {nome_imagem} (com {len(bboxes_originais)} caixas)...")

        for i in range(IMAGENS_POR_ORIGINAL):
            try:
                # 3. APLICAR A TRANSFORMAÇÃO
                augmented = transform(image=imagem_original, bboxes=bboxes_originais, class_labels=labels_originais)
                
                imagem_transformada = augmented['image']
                bboxes_transformados = augmented['bboxes']
                labels_transformados = augmented['class_labels']

                if not bboxes_transformados:
                    continue

                # 4. Gerar novos nomes
                novo_nome_base = f"{nome_base}_aug_{i+1}"
                novo_caminho_img = os.path.join(PASTA_AUMENTADA_IMG, f"{novo_nome_base}{ext_imagem}")
                novo_caminho_lbl = os.path.join(PASTA_AUMENTADA_LBL, f"{novo_nome_base}.txt")

                # 5. Salvar a nova imagem
                imagem_transformada_bgr = cv2.cvtColor(imagem_transformada, cv2.COLOR_RGB2BGR)
                cv2.imwrite(novo_caminho_img, imagem_transformada_bgr)

                # 6. Salvar as novas labels
                salvar_yolo_labels(novo_caminho_lbl, bboxes_transformados, labels_transformados)
                
                contador_total += 1
            except Exception as e:
                print(f"Erro ao transformar {nome_imagem} (iteração {i}): {e}")

    print(f"\nConcluído! {contador_total} novas imagens (e labels) geradas.")
    print(f"Elas estão salvas dentro de '{NOME_PASTA_DATASET}/train_augmented/'.")

# --- Executar a função ---
if __name__ == "__main__":
    aumentar_dataset_yolo()