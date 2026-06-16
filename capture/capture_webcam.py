import cv2
import time
import os


# ===== CONFIGURAÇÃO =====
image_number = 5      #quantidade de imagens que queremos
total_time = 10       #tepo total para a captura
capture_folder = "capturas" 

# --- Cálculo do intervalo entre as capturas ---
capture_interval = total_time / image_number 

# --- Cria a pasta de destino (se ela não existir) ---
os.makedirs(capture_folder, exist_ok=True)

# --- Inicialização da Webcam ---
cap = cv2.VideoCapture(0) # "0" -> webcam padrão "1" -> webam externa

if not cap.isOpened():
    print("Erro: Não foi possível abrir a webcam.")
    exit()

print(f"Iniciando captura de {image_number} imagens em {total_time} segundos.")
print(f"Um frame será capturado a cada {capture_interval:.2f} segundos.")
print("Pressione 'Esc' para sair a qualquer momento.")

image_counter = 0
previous_time = time.time() # Inicia o contador de tempo  ==== MESMA LÓGICA DO MILLIS EM C++

# --- Funcionameto geral ---
try:
    while (image_counter < image_number):
        #Lê o frame atual da webcam
        ret, frame = cap.read()
        if not ret:
            print("Erro: Não foi possível ler o frame.")
            break

        # --- FLIP HORIZONTAL ---
        # O '1' inverte a imagem horizontalmente (modo espelho)
        frame = cv2.flip(frame, 1)
        # ---------------------------------- 

        cv2.imshow("Feed da webcam -- Pressione 'Esc' para sair", frame)
            #Verifica se é hora de capturar
        current_time = time.time()

        if (current_time - previous_time) >= capture_interval: # Mesma Lógica do MILLIS() do C++

            # Salva o tempo atual para a próxima verificação
            previous_time = current_time

            image_counter += 1 #Incromenta o contador
            
            file_name = os.path.join(capture_folder, f"capture_{image_counter}.jpg")
            
            # Converte para o caminho absoluto (para o print)
            absolute_path = os.path.abspath(file_name)
            
            #Salva o frame como uma imagem
            cv2.imwrite(file_name, frame)
            
            print(f"Imagem {image_counter}/{image_number} capturada e salva em:")
            print(f"{absolute_path}")


        key = cv2.waitKey(1)

        if key == 27:  # 27 é o código da tecla 'Esc'
            print("Captura interrompida pelo usuário.")
            break
finally:
    # Adiciona a limpeza
    print("\nEncerrando e limpando recursos...")
    cap.release()
    cv2.destroyAllWindows()

print("Captura concluída.")