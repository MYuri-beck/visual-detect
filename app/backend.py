from capture.interface import CV2_AVAILABLE
import cv2
import threading
import time
# from ultralytics import YOLO

class CameraManager:
    """Gerencia o feed de vídeo da webcam (apenas hardware)."""
    def __init__(self):
        self.cap = None
        self.frame = None
        self.is_running = False
        self.lock = threading.Lock()

    def start(self, camera_index=0):
        if not CV2_AVAILABLE:
            return False
        try:
            
        pass

    def stop(self):
        # Lógica para liberar a câmera
        pass

    def get_frame(self):
        # Retorna o frame atual com segurança
        pass

class VisionAnalyzer:
    """Gerencia a IA e processamento de imagem (YOLO)."""
    def __init__(self, model_path):
        self.model_path = model_path
        self.model = None
        # self.model = YOLO(model_path)
        
    def analyze_frame(self, frame):
        """Passa o frame na IA e retorna os resultados."""
        # result = self.model.predict(frame)
        # return result
        pass

class CaptureSession:
    """Gerencia o fluxo do exame (quantas fotos, tempo, pastas de salvar)."""
    def __init__(self, camera: CameraManager, analyzer: VisionAnalyzer):
        self.camera = camera
        self.analyzer = analyzer
        
    def start_exam(self, on_finish_callback):
        """Inicia a captura das fotos em background e chama o callback ao terminar."""
        pass
