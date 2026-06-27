import cv2
import os
from ultralytics import YOLO

# 1. Configurações de Pastas e Modelo
NOME_DO_TREINO = "Treino_5k__Dropout025_m" 
MODELO_PATH = os.path.join("..", "training", "runs", "detect", NOME_DO_TREINO, "weights", "best.pt")
pasta_sobrevivente = "reflexo_gica"
pasta_resultados = "resultados_sobrevivente"

os.makedirs(pasta_resultados, exist_ok=True)

print("=== INICIANDO VALIDAÇÃO CLÍNICA (CASOS REAIS) ===")

# 2. Carregar o modelo
try:
    modelo = YOLO(MODELO_PATH)
    print("Modelo YOLO carregado com sucesso.\n")
except Exception as e:
    print(f"Erro ao carregar o modelo: {e}")
    exit()

# 3. Analisar cada imagem da sobrevivente
for nome_arquivo in os.listdir(pasta_sobrevivente):
    caminho_imagem = os.path.join(pasta_sobrevivente, nome_arquivo)
    
    # Pula arquivos que não sejam imagens
    if not nome_arquivo.lower().endswith(('.png', '.jpg', '.jpeg')):
        continue

    print(f"Analisando fotografia clínica: {nome_arquivo}...")
    
    # Faz a detecção
    resultados = modelo.predict(caminho_imagem, device="cpu", verbose=False)
    resultado = resultados[0]
    
    # Desenha as caixas (Bounding Boxes) na imagem
    imagem_com_deteccao = resultado.plot()
    
    # Salva a imagem processada na pasta de resultados
    caminho_salvar = os.path.join(pasta_resultados, f"{NOME_DO_TREINO}_laudo_{nome_arquivo}")
    cv2.imwrite(caminho_salvar, imagem_com_deteccao)
    
    # 4. Impressão do Laudo para o Relatório
    if len(resultado.boxes) > 0:
        for box in resultado.boxes:
            confianca = float(box.conf[0]) * 100
            nome_classe = modelo.names[int(box.cls[0])]
            
            # Formatação visual para destacar o sucesso da IA
            print(f"   SUCESSO! Anomalia identificada.")
            print(f"  -> Diagnóstico da IA: {nome_classe.upper()}")
            print(f"  -> Nível de Confiança: {confianca:.1f}%")
            print(f"  -> Imagem salva em: {caminho_salvar}\n")
    else:
        print("Nenhuma anomalia detectada nesta imagem (Falso Negativo ou sem visibilidade).\n")

print("=== VALIDAÇÃO CONCLUÍDA ===")