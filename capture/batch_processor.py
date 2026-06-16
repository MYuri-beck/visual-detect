import cv2
import time
import os
from ultralytics import YOLO
from datetime import datetime #

# ===== 1. CONFIGURAÇÃO =====
image_number = 10
total_time = 10
capture_folder = "capturas"  # <--Pasta para as capturas
analyzed_folder = "capturas_analisadas" # <--Pasta para os resultados

# --- CONFIGURAÇÃO DO MODELO ---
NOME_DO_TREINO = "treino_300_dropout_m" # <-- Confirmar este nome
MODELO_PATH = os.path.join("..", "training", "runs", "detect", NOME_DO_TREINO, "weights", "best.pt")

# --- Cálculo do intervalo ---
capture_interval = total_time / image_number #
 
# --- Cria as pastas de destino ---
os.makedirs(capture_folder, exist_ok=True) # <--Cria a pasta de capturas
os.makedirs(analyzed_folder, exist_ok=True) # <--Cria a pasta de análise

# --- Carregar o Modelo YOLO (na CPU) ---
print(f"Carregando modelo: {MODELO_PATH}...")
try:
    if not os.path.exists(MODELO_PATH):
        print(f"ERRO: Modelo não encontrado em '{MODELO_PATH}'")
        exit()
    model = YOLO(MODELO_PATH)
    print("Modelo carregado com sucesso.")
except Exception as e:
    # Se o modelo estiver corrompido, isto irá apanhar o erro 'Ran out of input'
    print(f"Erro ao carregar o modelo: {e}")
    exit()

# --- Inicialização da Webcam ---
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Erro: Não foi possível abrir a webcam.")
    exit()

lista_de_imagens_capturadas = []

# --- FUNCIONAMENTO GERAL ---
try:
    
    # --- LOOP 1: PRÉ-VISUALIZAÇÃO (ESPERANDO 's') ---
    print("\n--- PRÉ-VISUALIZAÇÃO ---")
    print("Posicione-se. Presione 's' para começar a captura ou 'Esc' para sair.")
    
    captura_iniciada = False

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Erro ao ler frame.")
            break
        
        frame = cv2.flip(frame, 1)
        
        
        cv2.putText(frame, "PRONTO. pressione 'S' para iniciar.", (20, 40), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        cv2.imshow("Feed da webcam -- Pressione 's' para iniciar", frame)

        key = cv2.waitKey(1) & 0xFF

        if key == ord('s'):
            captura_iniciada = True
            print(f"\n--- FASE 1: Iniciando captura de {image_number} imagens... ---")
            break 
        
        if key == 27: # 'Esc'
            print("Captura cancelada pelo usuário.")
            break 

    # --- FIM DO LOOP 1 ---


    # --- LOOP 2: CAPTURA PROGRAMADA ---
    if captura_iniciada:
        
        session_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        image_counter = 0
        previous_time = time.time()

        while (image_counter < image_number):
            ret, frame = cap.read()
            if not ret:
                print("Erro ao ler frame.")
                break
            
            frame = cv2.flip(frame, 1)
            
           
            cv2.imshow("Feed da webcam -- Prima 's' para iniciar", frame)

            current_time = time.time()
            
            if (current_time - previous_time) >= capture_interval:
                previous_time = current_time
                image_counter += 1
                
                base_filename = f"{session_timestamp}_capture_{image_counter}.jpg"
                file_name = os.path.join(capture_folder, base_filename)
                
                absolute_path = os.path.abspath(file_name)
                
                cv2.imwrite(file_name, frame)
                print(f"Imagem {image_counter}/{image_number} capturada e salva em:")
                print(f"{absolute_path}")
                
                lista_de_imagens_capturadas.append((file_name, base_filename))

            if cv2.waitKey(1) & 0xFF == 27:
                print("Captura interrompida pelo usuário.")
                break
        
        print("\n--- FASE 1 CONCLUÍDA: Captura finalizada. ---")


finally:
    # --- LIMPEZA DA CÂMERA ---
    print("\nEncerrando e limpando recursos da câmera...")
    cap.release()
    cv2.destroyAllWindows()
