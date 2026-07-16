"""
backend.py — Camada de lógica do VisualDetect
===============================================
Responsável por:
  - Gerenciar a câmera em thread separada (CameraManager)
  - Carregar e executar o modelo YOLO (VisionAnalyzer)
  - Coordenar o fluxo de captura e análise de um exame (CaptureSession)

Este arquivo não importa nada de outros módulos do projeto VisualDetect.
As únicas dependências externas são bibliotecas de terceiros (cv2, ultralytics).
"""

import os
import cv2
import time
import threading
from datetime import datetime


# ============================================================================
# DISPONIBILIDADE DE DEPENDÊNCIAS OPCIONAIS
# ============================================================================

# Tenta importar cv2 — câmera e feed ficam desabilitados se não estiver instalado
try:
    import cv2
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False
    print("[AVISO] opencv-python não encontrado — câmera desabilitada.")

# Tenta importar ultralytics — análise YOLO fica desabilitada se não estiver instalada
try:
    from ultralytics import YOLO
    YOLO_AVAILABLE = True
except ImportError:
    YOLO_AVAILABLE = False
    print("[AVISO] ultralytics não encontrado — análise YOLO desabilitada.")


# ============================================================================
# CONFIGURAÇÃO
# ============================================================================
# Estes valores são sobrescritos pelo main.py quando a aplicação sobe.
# Se rodar este módulo diretamente, os valores abaixo são usados como padrão.

# Pasta onde as imagens capturadas são salvas antes da análise
# PARA ALTERAR: mude a string abaixo ou passe capture_folder= para CaptureSession
CAPTURE_FOLDER_DEFAULT = "capturas_voluntarios_analisar"

# Pasta onde as imagens analisadas (com anotações YOLO) são salvas
# PARA ALTERAR: mude a string abaixo ou passe analyzed_folder= para CaptureSession
ANALYZED_FOLDER_DEFAULT = "capturas_analisadas_voluntarios"


# ============================================================================
# GERENCIADOR DE CÂMERA
# ============================================================================

class CameraManager:
    """Captura frames da webcam em background para não travar a UI."""

    def __init__(self):
        self._cap = None
        self._frame = None
        self._lock = threading.Lock()
        self._running = False

    # --- controle ---

    def start(self, index=0):
        """Abre a câmera e inicia a thread de captura contínua."""
        if not CV2_AVAILABLE:
            return False
        try:
            self._cap = cv2.VideoCapture(index)
            if not self._cap.isOpened():
                print("[AVISO] Câmera não encontrada.")
                return False
            self._running = True
            threading.Thread(target=self._loop, daemon=True).start()
            return True
        except Exception as e:
            print(f"[ERRO] Câmera: {e}")
            return False

    def stop(self):
        """Para a thread e libera o hardware da câmera."""
        self._running = False
        if self._cap:
            self._cap.release()
            self._cap = None

    @property
    def available(self):
        """True se a câmera está aberta e pronta para captura."""
        return self._cap is not None and self._cap.isOpened()

    # --- leitura ---

    def get_frame(self):
        """Retorna o frame BGR mais recente (numpy array) ou None."""
        with self._lock:
            return self._frame.copy() if self._frame is not None else None

    # --- loop interno (roda em thread separada) ---

    def _loop(self):
        """Lê frames continuamente e guarda o mais recente no buffer."""
        while self._running:
            if self._cap and self._cap.isOpened():
                ok, frame = self._cap.read()
                if ok:
                    # Espelha horizontalmente para parecer espelho natural
                    frame = cv2.flip(frame, 1)
                    with self._lock:
                        self._frame = frame
            time.sleep(0.033)  # ~30 FPS


# ============================================================================
# ANALISADOR DE VISÃO (YOLO)
# ============================================================================

class VisionAnalyzer:
    """Carrega o modelo YOLO e processa imagens capturadas."""

    def __init__(self, model_path):
        self.model_path = model_path
        self.model = None
        self._loading = False

    def load_sync(self):
        """Carrega o modelo de forma síncrona (bloqueia quem chamar)."""
        self._loading = True
        self._load()
        self._loading = False

    def load_async(self, on_ready=None):
        """
        Carrega o modelo em background para não travar a UI.
        on_ready() é chamado na thread de carregamento quando terminar.
        Use after(0, ...) na UI para tocar em widgets com segurança.
        """
        def _worker():
            self._loading = True
            self._load()
            self._loading = False
            if on_ready:
                on_ready()
        threading.Thread(target=_worker, daemon=True).start()

    @property
    def is_loading(self):
        return self._loading

    def _load(self):
        """Carregamento interno — verifica existência do arquivo antes de tentar."""
        if not YOLO_AVAILABLE:
            return
        if not os.path.exists(self.model_path):
            print(f"[AVISO] Modelo não encontrado: {self.model_path}")
            return
        try:
            self.model = YOLO(self.model_path)
            print(f"[OK] Modelo carregado: {self.model_path}")
        except Exception as e:
            print(f"[ERRO] Falha ao carregar modelo: {e}")

    @property
    def available(self):
        """True se o modelo foi carregado com sucesso."""
        return self.model is not None

    def analyze_file(self, image_path, output_path):
        """
        Analisa uma imagem salva em disco e salva o resultado anotado em output_path.
        Retorna lista de detecções no formato [(label, confianca), ...].
        Retorna lista vazia se o modelo não estiver disponível.
        """
        if not self.available:
            return []
        try:
            results = self.model.predict(image_path, device="cpu", verbose=False)
            result = results[0]
            # Salva a imagem com as anotações do YOLO desenhadas
            cv2.imwrite(output_path, result.plot())

            detections = []
            for b in result.boxes:
                label = self.model.names[int(b.cls[0])]
                conf = float(b.conf[0])
                detections.append((label, conf))
            return detections
        except Exception as e:
            print(f"[ERRO] Análise de arquivo: {e}")
            return []


# ============================================================================
# SESSÃO DE CAPTURA
# ============================================================================

class CaptureSession:
    """
    Coordena o fluxo completo de um exame:
    captura periódica de frames, análise YOLO pós-exame e callbacks de progresso.

    Parâmetros opcionais de configuração de pasta (sobrescrevem os padrões globais):
      capture_folder  : pasta onde salvar os JPEGs brutos capturados
      analyzed_folder : pasta onde salvar as imagens com anotações YOLO
    """

    def __init__(self, camera: CameraManager, analyzer: VisionAnalyzer,
                 capture_folder=None, analyzed_folder=None):
        self.camera = camera
        self.analyzer = analyzer

        # Usa as pastas passadas por parâmetro ou cai nos padrões globais
        # PARA ALTERAR as pastas: passe capture_folder= e analyzed_folder= ao instanciar
        self.CAPTURE_FOLDER = capture_folder or CAPTURE_FOLDER_DEFAULT
        self.ANALYZED_FOLDER = analyzed_folder or ANALYZED_FOLDER_DEFAULT

        # Parâmetros do exame — ajustados pela UI (tela T2)
        self.image_number = 10   # quantidade de capturas por exame
        self.total_time = 10     # duração total do exame em segundos

        # Estado interno da sessão atual
        self.captured_images: list = []  # lista de (caminho_completo, nome_do_arquivo)
        self.session_ts = ""             # timestamp único por exame (formato YYYYMMDD_HHMMSS)

        # Cria as pastas se ainda não existirem
        os.makedirs(self.CAPTURE_FOLDER, exist_ok=True)
        os.makedirs(self.ANALYZED_FOLDER, exist_ok=True)

    # --- exame ---

    def start_exam(self, on_finish_callback=None, on_progress_callback=None):
        """
        Inicia a captura em background.

        Parâmetros
        ----------
        on_finish_callback   : callable(captured_images) — chamado ao final do exame
        on_progress_callback : callable(captured, total)  — chamado a cada foto tirada
        """
        self.session_ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.captured_images = []

        thread = threading.Thread(
            target=self._capture_loop,
            args=(on_finish_callback, on_progress_callback),
            daemon=True,
        )
        thread.start()

    def _capture_loop(self, on_finish, on_progress):
        """Loop de captura que roda em thread separada."""
        interval = self.total_time / max(self.image_number, 1)
        captured = 0
        last_snap = time.time()

        print(f"[Sessao] Iniciando — {self.image_number} fotos em {self.total_time}s")

        while captured < self.image_number:
            now = time.time()
            if (now - last_snap) >= interval:
                frame = self.camera.get_frame()
                if frame is not None:
                    captured += 1
                    fname = f"{self.session_ts}_capture_{captured}.jpg"
                    fpath = os.path.join(self.CAPTURE_FOLDER, fname)
                    cv2.imwrite(fpath, frame)
                    self.captured_images.append((fpath, fname))
                    last_snap = now
                    print(f"  [{captured}/{self.image_number}] -> {fpath}")

                    if on_progress:
                        on_progress(captured, self.image_number)

            time.sleep(0.05)

        print("[Sessao] Captura concluida.")

        # Análise YOLO roda aqui, antes de chamar o callback final
        if self.analyzer.available and self.captured_images:
            self._analyze_all()

        if on_finish:
            on_finish(self.captured_images)

    def _analyze_all(self):
        """Analisa todas as imagens da sessão e salva os resultados anotados."""
        print(f"\n--- Analise YOLO: {len(self.captured_images)} imagens ---")
        for fpath, fname in self.captured_images:
            out_path = os.path.join(self.ANALYZED_FOLDER, f"analyzed_{fname}")
            detections = self.analyzer.analyze_file(fpath, out_path)
            if not detections:
                print(f"  {fname}: nenhuma deteccao")
            else:
                for label, conf in detections:
                    print(f"  {fname}: {label.upper()} ({conf * 100:.1f}%)")
        print("--- Analise concluida. ---\n")
