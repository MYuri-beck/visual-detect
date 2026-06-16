import cv2
import time
import os
from ultralytics import YOLO
from datetime import datetime

# ===== 1. CONFIGURAÇÃO =====
image_number = 10
total_time = 2
capture_folder = "capturas_voluntarios_analisar"  
analyzed_folder = "capturas_analisadas_voluntarios" 

# --- CONFIGURAÇÃO DO MODELO ---
NOME_DO_TREINO = "treio_yolov8m_fenecit2" 
MODELO_PATH = os.path.join("..", "trainings", "runs", "detect", NOME_DO_TREINO, "weights", "best.pt")

capture_interval = total_time / image_number

os.makedirs(capture_folder, exist_ok=True)
os.makedirs(analyzed_folder, exist_ok=True)

# --- Carregar o Modelo YOLO ---
print(f"A carregar o modelo: {MODELO_PATH}...")
try:
    if not os.path.exists(MODELO_PATH):
        print(f"ERRO: Modelo não encontrado em '{MODELO_PATH}'")
        exit()
    model = YOLO(MODELO_PATH)
    print("Modelo carregado com sucesso.")
except Exception as e:
    print(f"Erro ao carregar o modelo: {e}")
    exit()

cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Erro: Não foi possível abrir a webcam.")
    exit()

lista_de_imagens_capturadas = []

# ==========================================
# --- FASE 1: CAPTURA DE IMAGENS ---
# ==========================================
try:
    print("\n--- MODO DE CAPTURA CONTÍNUA ---")
    print("Posicione o voluntário. Pressione 's' para capturar uma sequência.")
    print("Repita o processo para quantas pessoas quiser.")
    print("Pressione 'Esc' a qualquer momento para encerrar e analisar todas as imagens.")
    
    capturando_agora = False
    image_counter = 0
    previous_time = 0
    session_timestamp = ""

    while True:
        ret, frame = cap.read()
        if not ret: break
        
        frame = cv2.flip(frame, 1)
        
        if not capturando_agora:
            # --- ESTADO 1: ESPERANDO ---
            cv2.putText(frame, "PRONTO: 's' para capturar | 'Esc' para analisar", (10, 30), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
            cv2.imshow("Feed da webcam", frame)

            key = cv2.waitKey(1) & 0xFF
            if key == ord('s'):
                capturando_agora = True
                image_counter = 0
                previous_time = time.time()
                # Gera um timestamp único para a sequência dessa pessoa
                session_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                print(f"\n--- INICIANDO CAPTURA DE {image_number} IMAGENS ---")
            
            elif key == 27: # Tecla Esc
                print("\n--- ENCERRANDO CAPTURAS E INDO PARA ANÁLISE ---")
                break 
                
        else:
            # --- ESTADO 2: CAPTURANDO SEQUÊNCIA ---
            cv2.putText(frame, f"Capturando... {image_counter}/{image_number}", (10, 30), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            cv2.imshow("Feed da webcam", frame)
            
            current_time = time.time()
            if (current_time - previous_time) >= capture_interval:
                previous_time = current_time
                image_counter += 1
                
                # Salva a imagem
                base_filename = f"captura_{session_timestamp}_{image_counter}.jpg"
                file_name = os.path.join(capture_folder, base_filename)
                
                cv2.imwrite(file_name, frame)
                print(f"Imagem {image_counter}/{image_number} guardada.")
                lista_de_imagens_capturadas.append((file_name, base_filename))
                
                # Quando terminar a sequência atual, volta para o estado de espera
                if image_counter >= image_number:
                    capturando_agora = False
                    print("-> Sequência finalizada! Chame o próximo e pressione 's' novamente.")
            
            # Permite interromper tudo com Esc mesmo durante uma captura
            if cv2.waitKey(1) & 0xFF == 27:
                print("\n--- CAPTURA INTERROMPIDA. INDO PARA ANÁLISE ---")
                break

finally:
    cap.release()
    cv2.destroyAllWindows()


# ==========================================
# --- FASE 2: ANÁLISE E NOMEAÇÃO AUTOMÁTICA ---
# ==========================================
if lista_de_imagens_capturadas:
    print(f"\n--- A INICIAR ANÁLISE DE {len(lista_de_imagens_capturadas)} IMAGENS ---")
    
    for caminho_imagem, base_filename in lista_de_imagens_capturadas:
        tempo_inicio = time.time()

        try:
            # Faz a inferência
            results = model.predict(caminho_imagem, device="cpu", verbose=False)
            result = results[0]
            imagem_analisada = result.plot() # Desenha a caixa no frame
            
            # ---------------------------------------------------------
            # NOMEAÇÃO AUTOMÁTICA
            # ---------------------------------------------------------
            if len(result.boxes) > 0:
                # Pega no ID da caixa com maior nível de confiança
                class_id = int(result.boxes[0].cls[0])
                
                # O modelo lê a sua lista ['reflexo-alterado', 'reflexo-normal']
                tag_resultado = model.names[class_id] 
            else:
                # Se a criança piscar ou não houver olho
                tag_resultado = "sem-deteccao"
            # ---------------------------------------------------------

            # Monta o nome do ficheiro final. 
            nome_arquivo_final = f"{tag_resultado}_analisado_{base_filename}"
            caminho_salvar_analise = os.path.join(analyzed_folder, nome_arquivo_final)
            
            # Guarda a foto com o diagnóstico no nome
            cv2.imwrite(caminho_salvar_analise, imagem_analisada)
            
            tempo_fim = time.time()
            tempo_total = tempo_fim - tempo_inicio
            
            print(f"\n-> Diagnóstico da IA: [{tag_resultado.upper()}]")
            print(f"-> Ficheiro guardado como: {nome_arquivo_final}")

        except Exception as e:
            print(f" -> Erro ao analisar a imagem {caminho_imagem}: {e}")

    print("\n--- PROCESSO TOTALMENTE CONCLUÍDO! ---")
else:
    print("\nNenhuma imagem foi capturada para analisar.")