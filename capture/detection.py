import cv2
from ultralytics import YOLO
import os

# --- CONFIGURAÇÃO DO MODELO ---
MODELO_PATH = "/home/visualdetectrb/Desktop/Rede_visualDetect/trainings/runs/detect/treino_YOLO8m_continuacao2/weights/best.pt"

# Verifica se o modelo existe antes de continuar
if not os.path.exists(MODELO_PATH):
    print(f"ERRO: Modelo não encontrado em '{MODELO_PATH}'")
    print("Verifique se o NOME_DO_TREINO está correto.")
    exit()

print(f"Carregando modelo: {MODELO_PATH}")

# Carrega o modelo e o envia para a CPU
model = YOLO(MODELO_PATH)

# --- ALTERAÇÃO 1 ---
model.to("cpu") #
# --- ALTERAÇÃO 2 ---
print("Modelo carregado na CPU. Iniciando webcam...") #

# --- 2. INICIALIZAÇÃO DA WEBCAM ---
cap = cv2.VideoCapture(0) # 0 para webcam padrão
if not cap.isOpened():
    print("Erro: Não foi possível abrir a webcam.")
    print("Verifique se ela não está em uso por outro app (Discord, Zoom, etc.)")
    exit()

print("Iniciando detecção em tempo real... Pressione 'Esc' para sair.")

# --- 3. LOOP DE DETECÇÃO EM TEMPO REAL ---
try:
    while True:
        # Lê o frame da webcam
        ret, frame = cap.read()
        if not ret:
            print("Erro: Não foi possível ler o frame.")
            break
        
        # Flipa a imagem
        frame = cv2.flip(frame, 1)

        # --- ANÁLISE DO YOLO (EM TEMPO REAL) ---
        # --- ALTERAÇÃO 3 ---
        # Roda a detecção na CPU
        results = model.predict(frame, device="cpu", verbose=False) #
        

        # 'results[0].plot()' é um atalho do Ultralytics
        # que desenha todas as caixas de detecção no frame
        frame_com_deteccoes = results[0].plot()

        # Mostra o frame resultante (com as detecções)
        cv2.imshow("Detecção em Tempo Real - Pressione 'Esc'", frame_com_deteccoes)

        # Tecla de saída (Esc)
        key = cv2.waitKey(1)
        if key == 27:
            print("Encerrando detecção.")
            break

finally:
    # --- 4. LIMPEZA ---
    print("Limpando recursos...")
    cap.release()
    cv2.destroyAllWindows()