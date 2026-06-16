import os
import matplotlib.pyplot as plt
from sklearn.metrics import roc_curve, auc
from ultralytics import YOLO
import csv
from pathlib import Path

# ===== CONFIGURAÇÃO =====
MODELO_PATH = r"C:\Users\yurim\Desktop\Software Visual Detect\VisualDetect\trainings\runs\detect\treio_yolov8m_fenecit2\weights\best.pt"

# Classe positiva na ROC: 1 = doente, 0 = saudável
PASTAS_DOENTES = [
    # Exemplo:
    # r"C:\caminho\pasta_so_doentes",
]

PASTAS_SAUDAVEIS = [
]

# Pastas mistas exigem gabarito por CSV.
# CSV com cabeçalho: arquivo,label
# label pode ser: 0/1, saudavel/doente, normal/alterado
PASTAS_MISTAS = [
]

# Fontes no formato YOLO (imagem + label .txt)
# Classe YOLO 0 = reflexo-alterado (doente), classe 1 = reflexo-normal (saudável)
DATASETS_YOLO = [
    {
        "images_dir": r"C:\Users\yurim\Desktop\Software Visual Detect\VisualDetect\trainings\valid\images",
        "labels_dir": r"C:\Users\yurim\Desktop\Software Visual Detect\VisualDetect\trainings\valid\labels",
    },
    {
        "images_dir": r"C:\Users\yurim\Desktop\Software Visual Detect\VisualDetect\trainings\test\images",
        "labels_dir": r"C:\Users\yurim\Desktop\Software Visual Detect\VisualDetect\trainings\test\labels",
    },
]

# Validação cruzada 10-fold: usa cada val.txt para inferir os labels YOLO correspondentes.
FOLDS_VAL_TXT = [
    rf"C:\Users\yurim\Desktop\Software Visual Detect\VisualDetect\Main\temp_kfold\fold_{i}\val.txt"
    for i in range(1, 11)
]

modelo = YOLO(MODELO_PATH)
y_verdadeiro = []  # Gabarito
y_scores = []      # Certeza da IA


def parse_label(valor):
    v = str(valor).strip().lower()
    if v in {"1", "doente", "alterado", "positivo", "pos"}:
        return 1
    if v in {"0", "saudavel", "saudável", "normal", "negativo", "neg"}:
        return 0
    raise ValueError(f"Rótulo inválido no CSV: {valor}")


def carregar_rotulos_csv(caminho_csv):
    if not os.path.exists(caminho_csv):
        raise FileNotFoundError(f"CSV de rótulos não encontrado: {caminho_csv}")

    rotulos = {}
    with open(caminho_csv, "r", encoding="utf-8-sig", newline="") as f:
        leitor = csv.DictReader(f)
        if "arquivo" not in leitor.fieldnames or "label" not in leitor.fieldnames:
            raise ValueError("CSV deve ter colunas: arquivo,label")
        for linha in leitor:
            nome = os.path.basename(linha["arquivo"]).strip()
            rotulos[nome] = parse_label(linha["label"])
    return rotulos

def avaliar_pasta(caminho, classe_real):
    print(f"Analisando pasta: {caminho}")
    for img_nome in os.listdir(caminho):
        if img_nome.lower().endswith(('.png', '.jpg', '.jpeg')):
            res = modelo(os.path.join(caminho, img_nome), verbose=False)[0]
            
            y_verdadeiro.append(classe_real)
            
            if len(res.boxes) > 0:
                conf = float(res.boxes[0].conf[0])
                classe_detectada = int(res.boxes[0].cls[0])
                
                # Se detectou 'alterado' (classe 0 no seu yaml), o score é a própria confiança
                # Se detectou 'normal', o score para ser 'alterado' é baixo (1 - conf)
                score = conf if classe_detectada == 0 else (1 - conf)
                y_scores.append(score)
            else:
                y_scores.append(0.0)


def avaliar_pasta_mista(caminho, csv_rotulos):
    print(f"Analisando pasta mista: {caminho}")
    rotulos = carregar_rotulos_csv(csv_rotulos)

    for img_nome in os.listdir(caminho):
        if not img_nome.lower().endswith((".png", ".jpg", ".jpeg")):
            continue

        if img_nome not in rotulos:
            print(f"[AVISO] Sem rótulo no CSV, ignorando: {img_nome}")
            continue

        classe_real = rotulos[img_nome]
        res = modelo(os.path.join(caminho, img_nome), verbose=False)[0]

        y_verdadeiro.append(classe_real)

        if len(res.boxes) > 0:
            conf = float(res.boxes[0].conf[0])
            classe_detectada = int(res.boxes[0].cls[0])

            # Classe 0 do detector = alterado (doente) no seu treinamento atual
            score = conf if classe_detectada == 0 else (1 - conf)
            y_scores.append(score)
        else:
            y_scores.append(0.0)


def classe_real_por_label_yolo(label_path):
    """Converte label YOLO em classe binária clínica (1=doente, 0=saudável)."""
    if not os.path.exists(label_path):
        return None

    classes = set()
    with open(label_path, "r", encoding="utf-8") as f:
        for linha in f:
            linha = linha.strip()
            if not linha:
                continue
            partes = linha.split()
            try:
                classes.add(int(partes[0]))
            except (ValueError, IndexError):
                continue

    if not classes:
        return None
    if 0 in classes:
        return 1
    if 1 in classes:
        return 0
    return None


def avaliar_dataset_yolo(images_dir, labels_dir):
    print(f"Analisando dataset YOLO: {images_dir}")
    for img_nome in os.listdir(images_dir):
        if not img_nome.lower().endswith((".png", ".jpg", ".jpeg")):
            continue

        label_nome = Path(img_nome).with_suffix(".txt").name
        label_path = os.path.join(labels_dir, label_nome)
        classe_real = classe_real_por_label_yolo(label_path)

        if classe_real is None:
            print(f"[AVISO] Label ausente/inválido, ignorando: {img_nome}")
            continue

        res = modelo(os.path.join(images_dir, img_nome), verbose=False)[0]
        y_verdadeiro.append(classe_real)

        if len(res.boxes) > 0:
            conf = float(res.boxes[0].conf[0])
            classe_detectada = int(res.boxes[0].cls[0])
            score = conf if classe_detectada == 0 else (1 - conf)
            y_scores.append(score)
        else:
            y_scores.append(0.0)


def avaliar_fold_val_txt(caminho_val_txt):
    if not os.path.exists(caminho_val_txt):
        return

    print(f"Analisando fold (val.txt): {caminho_val_txt}")
    with open(caminho_val_txt, "r", encoding="utf-8") as f:
        imagens = [linha.strip() for linha in f if linha.strip()]

    for img_path in imagens:
        if not os.path.exists(img_path):
            print(f"[AVISO] Imagem não encontrada, ignorando: {img_path}")
            continue

        img_path_obj = Path(img_path)
        label_path = str(img_path_obj.parent.parent / "labels" / f"{img_path_obj.stem}.txt")
        classe_real = classe_real_por_label_yolo(label_path)

        if classe_real is None:
            print(f"[AVISO] Label ausente/inválido, ignorando: {img_path_obj.name}")
            continue

        res = modelo(img_path, verbose=False)[0]
        y_verdadeiro.append(classe_real)

        if len(res.boxes) > 0:
            conf = float(res.boxes[0].conf[0])
            classe_detectada = int(res.boxes[0].cls[0])
            score = conf if classe_detectada == 0 else (1 - conf)
            y_scores.append(score)
        else:
            y_scores.append(0.0)

# 1. Coletar Dados
for pasta in PASTAS_DOENTES:
    avaliar_pasta(pasta, 1)

for pasta in PASTAS_SAUDAVEIS:
    avaliar_pasta(pasta, 0)

for item in PASTAS_MISTAS:
    avaliar_pasta_mista(item["pasta"], item["csv_rotulos"])

for ds in DATASETS_YOLO:
    avaliar_dataset_yolo(ds["images_dir"], ds["labels_dir"])

for val_txt in FOLDS_VAL_TXT:
    avaliar_fold_val_txt(val_txt)

if len(y_verdadeiro) == 0:
    raise RuntimeError("Nenhuma imagem válida encontrada para avaliar.")

if len(set(y_verdadeiro)) < 2:
    raise RuntimeError("A ROC precisa de exemplos das duas classes (0 e 1).")

# 2. Calcular Métricas
fpr, tpr, _ = roc_curve(y_verdadeiro, y_scores)
roc_auc = auc(fpr, tpr)

# 3. Gerar e Salvar o Gráfico
plt.figure(figsize=(8, 6))
plt.plot(fpr, tpr, color='darkorange', lw=2, label=f'Curva ROC (AUC = {roc_auc:.3f})')
plt.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--') # Linha de sorte
plt.xlim([0.0, 1.0])
plt.ylim([0.0, 1.05])
plt.xlabel('Taxa de Falsos Positivos (1 - Especificidade)')
plt.ylabel('Taxa de Verdadeiros Positivos (Sensibilidade)')
plt.title('Validação Clínica VisualDetect - Curva ROC')
plt.legend(loc="lower right")
plt.grid(alpha=0.3)

plt.savefig("grafico_roc_auc_final.png", dpi=300)
print(f"\n Gráfico ROC gerado com sucesso! AUC: {roc_auc:.3f}")
plt.show()