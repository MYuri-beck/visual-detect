import sys
from backend import CameraManager, VisionAnalyzer, CaptureSession
from ui import VisualDetectUI

def main():
    print("Iniciando VisualDetect (Modo Refatorado)...")
    
    # 1. Instanciar as classes do Backend (O Cérebro)
    camera = CameraManager()
    analyzer = VisionAnalyzer(model_path="../training/runs/detect/Treino_5k__Dropout025_m/weights/best.pt")
    
    # Inicia a câmera em segundo plano
    # camera.start()
    
    session = CaptureSession(camera, analyzer)
    
    # 2. Instanciar a Interface Gráfica, injetando a sessão nela
    app = VisualDetectUI(backend_session=session)
    
    # 3. Lógica para Kiosk (Raspberry Pi)
    if "--fullscreen" in sys.argv:
        app.attributes("-fullscreen", True)
        
    # 4. Iniciar o Loop Visual
    app.mainloop()
    
    # 5. Encerrar hardware de forma limpa ao fechar a janela
    print("Encerrando...")
    camera.stop()

if __name__ == "__main__":
    main()
