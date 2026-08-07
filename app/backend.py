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
import json


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

    def start(self, index=1):
        """Abre a câmera e inicia a thread de captura contínua."""
        # Guard: se já estiver rodando, não abre uma segunda instância
        if self._running and self._cap is not None and self._cap.isOpened():
            return True
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

        # Callbacks de progresso de análise — definidos dinamicamente pela tela T4b
        # Permitem que T4b receba atualizações da thread de análise YOLO
        self._ui_analyze_progress_cb = None  # callable(idx, total, fname)
        self._ui_analyze_finish_cb   = None  # callable(captured_images)

        # Pasta do último exame analisado (para referência da galeria)
        self.last_analyzed_folder: str = ""

        # Cria as pastas se ainda não existirem
        os.makedirs(self.CAPTURE_FOLDER, exist_ok=True)
        os.makedirs(self.ANALYZED_FOLDER, exist_ok=True)

    # --- exame ---

    def start_exam(self, on_finish_callback=None, on_progress_callback=None,
                   on_capture_done_callback=None):
        """
        Inicia a captura em background.

        Parâmetros
        ----------
        on_finish_callback       : callable(captured_images) — chamado ao final da análise YOLO
        on_progress_callback     : callable(captured, total)  — chamado a cada foto tirada
        on_capture_done_callback : callable(captured_images) — chamado quando todas as fotos
                                   foram tiradas, ANTES da análise YOLO começar. Usado pela
                                   UI para trocar para a tela T4b antes do processamento.
        """
        self.session_ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.captured_images = []
        self._ui_analyze_progress_cb = None      # T4b registra ao ser exibida
        self._ui_analyze_finish_cb   = on_finish_callback  # fallback; T4b pode sobrescrever

        thread = threading.Thread(
            target=self._capture_loop,
            args=(on_progress_callback, on_capture_done_callback),
            daemon=True,
        )
        thread.start()

    def _capture_loop(self, on_progress, on_capture_done):
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

        # Sinaliza que a captura terminou — a UI troca para T4b
        if on_capture_done:
            on_capture_done(self.captured_images)

        # Aguarda a UI trocar para T4b e registrar os callbacks de análise.
        # 400 ms e mais que suficiente para o tkinter processar a troca de tela.
        time.sleep(0.4)

        # Análise YOLO roda com a T4b já ativa para receber os callbacks
        if self.analyzer.available and self.captured_images:
            self._analyze_all()

        # Notifica conclusão (T4b pode ter sobrescrito _ui_analyze_finish_cb)
        if self._ui_analyze_finish_cb:
            self._ui_analyze_finish_cb(self.captured_images)

    def _analyze_all(self):
        """
        Analisa todas as imagens da sessão, salva os resultados em subpasta
        organizada por exame e grava um detections.json com as detecções.
        Subpasta: ANALYZED_FOLDER / "Exame DD-MM-YY - HH:MM" / "Analise NN.jpg"
        """
        total = len(self.captured_images)
        print(f"\n--- Analise YOLO: {total} imagens ---")

        # Cria subpasta com nome legível para a galeria
        exam_dt   = datetime.strptime(self.session_ts, "%Y%m%d_%H%M%S")
        exam_name = exam_dt.strftime("Exame %d-%m-%y - %H-%M")
        exam_folder = os.path.join(self.ANALYZED_FOLDER, exam_name)
        os.makedirs(exam_folder, exist_ok=True)
        self.last_analyzed_folder = exam_folder

        detections_map: dict = {}

        for i, (fpath, fname) in enumerate(self.captured_images):
            out_name = f"Analise {i + 1:02d}.jpg"
            out_path = os.path.join(exam_folder, out_name)
            detections = self.analyzer.analyze_file(fpath, out_path)

            detections_map[out_name] = [
                {"label": label, "conf": round(float(conf), 4)}
                for label, conf in detections
            ]

            if not detections:
                print(f"  {out_name}: nenhuma deteccao")
            else:
                for label, conf in detections:
                    print(f"  {out_name}: {label.upper()} ({conf * 100:.1f}%)")

            # Notifica a tela T4b do progresso (callback registrado dinamicamente)
            if self._ui_analyze_progress_cb:
                self._ui_analyze_progress_cb(i + 1, total, out_name)

        # Salva detecções como JSON para uso na galeria
        json_path = os.path.join(exam_folder, "detections.json")
        try:
            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(detections_map, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"[AVISO] Falha ao salvar detections.json: {e}")

        print("--- Analise concluida. ---\n")

    def get_exam_gallery(self) -> list:
        """
        Lê a pasta de exames analisados e retorna a estrutura de galeria.

        Retorna lista de dicts (mais recente primeiro):
          name       : nome da pasta  (ex: "Exame 03-08-26 - 14:35")
          folder     : caminho absoluto da pasta
          images     : lista de caminhos absolutos dos .jpg (ordenada)
          detections : dict {"Analise NN.jpg": [{"label": ..., "conf": ...}]}
        """
        result: list = []
        if not os.path.exists(self.ANALYZED_FOLDER):
            return result

        try:
            entries = sorted(os.listdir(self.ANALYZED_FOLDER), reverse=True)
        except Exception:
            return result

        for entry in entries:
            folder_path = os.path.join(self.ANALYZED_FOLDER, entry)
            if not os.path.isdir(folder_path) or not entry.startswith("Exame "):
                continue

            try:
                images = sorted([
                    os.path.join(folder_path, f)
                    for f in os.listdir(folder_path)
                    if f.lower().endswith((".jpg", ".jpeg", ".png"))
                    and f.startswith("Analise")
                ])
            except Exception:
                images = []

            detections: dict = {}
            json_path = os.path.join(folder_path, "detections.json")
            if os.path.exists(json_path):
                try:
                    with open(json_path, "r", encoding="utf-8") as f:
                        detections = json.load(f)
                except Exception:
                    pass

            if images:
                result.append({
                    "name":       entry,
                    "folder":     folder_path,
                    "images":     images,
                    "detections": detections,
                })

        return result
