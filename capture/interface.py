"""
interface.py — Interface Gráfica do VisualDetect
=================================================
Equipamento de Triagem do Reflexo Ocular

Display alvo: 800×480 (DSI Raspberry Pi 4)
Navegação:    ESP32 HID (← → ↑ ↓ ENTER)

Telas:
  T0  Info SENAI/NUDEP
  T1  Splash VisualDetect
  T2  Configuração (modo wizard — um campo por vez)
  T3  Revisão + Feed da câmera
  T4  Capturando (automático, botões bloqueados)
  T5  Exame concluído

Uso:
  python interface.py              # janela 800×480
  python interface.py --fullscreen # tela cheia (Raspberry Pi)

Autores: Yuri Mendes | Andrei Krug
"""

import sys
import os
import time
import threading
import tkinter as tk
from datetime import datetime

try:
    import customtkinter as ctk
except ImportError:
    print("ERRO: customtkinter não encontrado.")
    print("Instale com:  pip install customtkinter")
    sys.exit(1)

try:
    import cv2
    from PIL import Image, ImageTk
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False
    print("[AVISO] opencv-python ou Pillow não encontrado — câmera desabilitada.")

try:
    from ultralytics import YOLO
    YOLO_AVAILABLE = True
except ImportError:
    YOLO_AVAILABLE = False
    print("[AVISO] ultralytics não encontrado — análise YOLO desabilitada.")


# ============================================================================
# CONFIGURAÇÃO
# ============================================================================

# Resolução do display
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 480

# Modelo YOLO
NOME_DO_TREINO = "Treino_5k__Dropout025_m"
MODELO_PATH = os.path.join(
    os.path.dirname(__file__), "..", "training", "runs",
    "detect", NOME_DO_TREINO, "weights", "best.pt"
)

# Pastas de saída
CAPTURE_FOLDER = "capturas_voluntarios_analisar"
ANALYZED_FOLDER = "capturas_analisadas_voluntarios"

# Paleta de cores (roxo escuro + verde + âmbar)
C = {
    "bg":              "#0d0b1a",
    "bg_card":         "#1a1533",
    "bg_card_light":   "#252040",
    "bg_field":        "#1e1940",
    "border":          "#2d2755",
    "border_active":   "#00e676",
    "green":           "#00e676",
    "green_dark":      "#00c853",
    "white":           "#ffffff",
    "text2":           "#9e9ab8",
    "muted":           "#5c5880",
    "amber":           "#ffc107",
    "red":             "#ff1744",
    "purple":          "#7c4dff",
    "purple_light":    "#b388ff",
    "btn_off":         "#2a2550",
    "btn_off_border":  "#3d3670",
    "black":           "#000000",
    "transparent":     "transparent",
}


# ============================================================================
# GERENCIADOR DE CÂMERA  (thread separada)
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
        self._running = False
        if self._cap:
            self._cap.release()

    @property
    def available(self):
        return self._cap is not None and self._cap.isOpened()

    # --- leitura ---

    def get_frame(self):
        """Retorna o frame BGR mais recente (numpy) ou None."""
        with self._lock:
            return self._frame.copy() if self._frame is not None else None

    def get_photo(self, width, height):
        """Retorna um ImageTk.PhotoImage redimensionado para exibição."""
        frame = self.get_frame()
        if frame is None:
            return None
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        rgb = cv2.resize(rgb, (width, height))
        return ImageTk.PhotoImage(Image.fromarray(rgb))

    # --- loop interno ---

    def _loop(self):
        while self._running:
            if self._cap and self._cap.isOpened():
                ok, frame = self._cap.read()
                if ok:
                    frame = cv2.flip(frame, 1)
                    with self._lock:
                        self._frame = frame
            time.sleep(0.033)  # ~30 FPS


# ============================================================================
# CLASSE BASE PARA TELAS
# ============================================================================

class BaseScreen(ctk.CTkFrame):
    """Classe base que todas as telas herdam."""

    def __init__(self, app, **kw):
        kw.setdefault("fg_color", C["bg"])
        super().__init__(app, **kw)
        self.app = app
        self._after_ids: list[str] = []

    # after() seguro: guarda IDs para cancelar na troca de tela
    def safe_after(self, ms, callback):
        aid = self.after(ms, callback)
        self._after_ids.append(aid)
        return aid

    def cleanup(self):
        for aid in self._after_ids:
            try:
                self.after_cancel(aid)
            except Exception:
                pass
        self._after_ids.clear()

    def handle_key(self, event):
        """Sobrescrever nas subclasses."""
        pass


# ============================================================================
# T0 — INFORMAÇÕES INSTITUCIONAIS  (SENAI / NUDEP)
# ============================================================================

class ScreenT0(BaseScreen):

    def __init__(self, app):
        super().__init__(app)
        self._build()

    @staticmethod
    def _load_ctk_image(path, max_w, max_h):
        """Carrega PNG (com ou sem transparência) como CTkImage."""
        try:
            img = Image.open(path).convert("RGBA")
            img.thumbnail((max_w, max_h), Image.LANCZOS)
            return ctk.CTkImage(light_image=img, dark_image=img,
                                size=(img.width, img.height))
        except Exception as e:
            print(f"[AVISO] Logo não carregada: {e}")
            return None

    def _build(self):
        box = ctk.CTkFrame(self, fg_color=C["transparent"])
        box.place(relx=0.5, rely=0.5, anchor="center")

        # --- Logo NUDEP branca (fundo transparente) ---
        _NUDEP_PNG = os.path.join(
            os.path.dirname(__file__), "..",
            "docs", "interface", "Icons_logos", "logo - NUDEP_branco_png.png",
        )
        _ctk_img = self._load_ctk_image(_NUDEP_PNG, 260, 130)
        if _ctk_img:
            ctk.CTkLabel(box, image=_ctk_img, text="").pack(pady=(0, 24))
        else:
            ctk.CTkLabel(
                box, text="[ SENAI / NUDEP ]",
                font=ctk.CTkFont(size=18), text_color=C["muted"],
            ).pack(pady=(0, 24))

        # Instituição
        ctk.CTkLabel(
            box,
            text="Centro de Formação Profissional SENAI\nPlínio Gilberto Kröeff",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=C["white"], justify="center",
        ).pack(pady=(0, 10))

        # Curso
        ctk.CTkLabel(
            box, text="Curso Técnico em Desenvolvimento de Sistemas",
            font=ctk.CTkFont(size=15), text_color=C["text2"], justify="center",
        ).pack(pady=(0, 25))

        # Autores
        ctk.CTkLabel(
            box, text="Autores:",
            font=ctk.CTkFont(size=14), text_color=C["green"],
        ).pack(pady=(0, 4))
        ctk.CTkLabel(
            box, text="Yuri Mendes  |  Andrei Krug",
            font=ctk.CTkFont(size=16, weight="bold"), text_color=C["white"],
        ).pack(pady=(0, 30))

        # Dica
        ctk.CTkLabel(
            box, text="Pressione ENTER para continuar",
            font=ctk.CTkFont(size=12), text_color=C["muted"],
        ).pack()

    def handle_key(self, event):
        if event.keysym == "Return":
            self.app.show_screen("t1")


# ============================================================================
# T1 — SPLASH  (logo + INICIAR)
# ============================================================================

class ScreenT1(BaseScreen):

    def __init__(self, app):
        super().__init__(app)
        self._build()

    @staticmethod
    def _load_ctk_image(path, max_w, max_h):
        """Carrega PNG (com ou sem transparência) como CTkImage."""
        try:
            img = Image.open(path).convert("RGBA")
            img.thumbnail((max_w, max_h), Image.LANCZOS)
            return ctk.CTkImage(light_image=img, dark_image=img,
                                size=(img.width, img.height))
        except Exception as e:
            print(f"[AVISO] Logo não carregada: {e}")
            return None

    def _build(self):
        # Card central
        card = ctk.CTkFrame(
            self, fg_color=C["bg_card"], corner_radius=16,
            border_width=1, border_color=C["border"],
        )
        card.place(relx=0.5, rely=0.5, anchor="center",
                   relwidth=0.88, relheight=0.88)

        # Versão
        ctk.CTkLabel(
            card, text="v1.0", font=ctk.CTkFont(size=11),
            text_color=C["muted"],
        ).place(relx=0.96, rely=0.05, anchor="ne")

        # Conteúdo central
        center = ctk.CTkFrame(card, fg_color=C["transparent"])
        center.place(relx=0.5, rely=0.45, anchor="center")

        # --- Logo VisualDetect PNG ---
        _VD_PNG = os.path.join(
            os.path.dirname(__file__), "..",
            "docs", "interface", "Icons_logos", "logo - VisualDetect_greenPupil_png-Photoroom.png",
        )
        
        # ========================================================
        # PARA ALTERAR O TAMANHO DA LOGO, MUDE OS VALORES ABAIXO:
        largura_logo = 300
        altura_logo = 150
        # ========================================================
        
        _ctk_img = self._load_ctk_image(_VD_PNG, largura_logo, altura_logo)
        
        if _ctk_img:
            # Exibe a logo em um Label
            ctk.CTkLabel(center, image=_ctk_img, text="").pack(pady=(0, 18))
        else:
            # Fallback caso a imagem não seja encontrada
            ctk.CTkLabel(
                center, text="👁", font=ctk.CTkFont(size=40),
                text_color=C["purple"],
            ).pack(pady=(0, 18))

        # Título
        ctk.CTkLabel(
            center, text="VISUAL DETECT",
            font=ctk.CTkFont(size=34, weight="bold"), text_color=C["white"],
        ).pack(pady=(0, 6))

        # Subtítulo
        ctk.CTkLabel(
            center, text="Equipamento de Triagem do Reflexo Ocular",
            font=ctk.CTkFont(size=14), text_color=C["text2"],
        ).pack(pady=(0, 28))

        # Botão INICIAR
        ctk.CTkButton(
            center, text="INICIAR",
            font=ctk.CTkFont(size=16, weight="bold"),
            fg_color=C["green"], hover_color=C["green_dark"],
            text_color=C["black"], corner_radius=20,
            width=170, height=44, state="disabled",
        ).pack(pady=(0, 8))

        ctk.CTkLabel(
            center, text="[ ENTER ]",
            font=ctk.CTkFont(size=11), text_color=C["muted"],
        ).pack()

    def handle_key(self, event):
        if event.keysym == "Return":
            self.app.show_screen("t2")


# ============================================================================
# T2 — CONFIGURAÇÃO  (modo wizard — um campo por vez)
# ============================================================================

class ScreenT2(BaseScreen):
    """
    Wizard de 2 passos:
      Passo 0 → Nº de capturas   (↑↓ ajusta, ENTER avança, ← volta)
      Passo 1 → Tempo total      (↑↓ ajusta, ENTER confirma, ← volta)
    """

    FIELDS = [
        {"label": "Nº DE CAPTURAS", "attr": "image_number",
         "mn": 1, "mx": 50, "unit": ""},
        {"label": "TEMPO TOTAL",    "attr": "total_time",
         "mn": 1, "mx": 120, "unit": " s"},
    ]

    def __init__(self, app):
        super().__init__(app)
        self.step = 0
        self._build()
        self._refresh()

    def _build(self):
        # ---- header ----
        hdr = ctk.CTkFrame(self, fg_color=C["transparent"], height=50)
        hdr.pack(fill="x", padx=30, pady=(20, 0))
        hdr.pack_propagate(False)

        ctk.CTkLabel(
            hdr, text="‹", font=ctk.CTkFont(size=26, weight="bold"),
            text_color=C["text2"],
        ).pack(side="left")
        ctk.CTkLabel(
            hdr, text="CONFIGURAÇÃO DO EXAME",
            font=ctk.CTkFont(size=18, weight="bold"), text_color=C["white"],
        ).pack(side="left", padx=15)

        self._lbl_step = ctk.CTkLabel(
            hdr, font=ctk.CTkFont(size=13), text_color=C["muted"],
        )
        self._lbl_step.pack(side="right")

        # ---- card central ----
        card = ctk.CTkFrame(
            self, fg_color=C["bg_card"], corner_radius=16,
            border_width=2, border_color=C["border_active"],
        )
        card.place(relx=0.5, rely=0.48, anchor="center",
                   relwidth=0.65, relheight=0.50)

        self._lbl_name = ctk.CTkLabel(
            card, font=ctk.CTkFont(size=16), text_color=C["text2"],
        )
        self._lbl_name.place(relx=0.5, rely=0.15, anchor="center")

        ctk.CTkLabel(
            card, text="▲", font=ctk.CTkFont(size=22), text_color=C["muted"],
        ).place(relx=0.5, rely=0.30, anchor="center")

        self._lbl_val = ctk.CTkLabel(
            card, font=ctk.CTkFont(size=56, weight="bold"),
            text_color=C["white"],
        )
        self._lbl_val.place(relx=0.5, rely=0.52, anchor="center")

        ctk.CTkLabel(
            card, text="▼", font=ctk.CTkFont(size=22), text_color=C["muted"],
        ).place(relx=0.5, rely=0.72, anchor="center")

        # Step dots
        self._dots_frame = ctk.CTkFrame(card, fg_color=C["transparent"])
        self._dots_frame.place(relx=0.5, rely=0.90, anchor="center")

        self._dots = []
        for i in range(len(self.FIELDS)):
            d = ctk.CTkFrame(
                self._dots_frame, width=10, height=10, corner_radius=5,
                fg_color=C["muted"],
            )
            d.pack(side="left", padx=4)
            self._dots.append(d)

        # ---- footer ----
        foot = ctk.CTkFrame(
            self, fg_color=C["bg_card_light"], corner_radius=8, height=40,
        )
        foot.pack(side="bottom", fill="x", padx=30, pady=15)
        foot.pack_propagate(False)

        self._lbl_hints = ctk.CTkLabel(
            foot, font=ctk.CTkFont(size=12), text_color=C["muted"],
        )
        self._lbl_hints.place(relx=0.5, rely=0.5, anchor="center")

    # --- atualização visual ---

    def _refresh(self):
        f = self.FIELDS[self.step]
        val = getattr(self.app, f["attr"])

        self._lbl_step.configure(text=f"Passo {self.step + 1} / {len(self.FIELDS)}")
        self._lbl_name.configure(text=f["label"])
        self._lbl_val.configure(text=f"{val}{f['unit']}")

        # dots
        for i, d in enumerate(self._dots):
            d.configure(fg_color=C["green"] if i == self.step else C["muted"])

        # hints
        if self.step == 0:
            self._lbl_hints.configure(
                text="↑ ↓  Ajustar      ENTER  Próximo      ←  Voltar"
            )
        else:
            self._lbl_hints.configure(
                text="↑ ↓  Ajustar      ENTER  Confirmar    ←  Voltar"
            )

    def _adjust(self, delta):
        f = self.FIELDS[self.step]
        cur = getattr(self.app, f["attr"])
        new = max(f["mn"], min(f["mx"], cur + delta))
        setattr(self.app, f["attr"], new)
        self._refresh()
        # flash
        self._lbl_val.configure(text_color=C["green"])
        self.safe_after(
            200, lambda: self._lbl_val.configure(text_color=C["white"])
        )

    # --- teclado ---

    def handle_key(self, event):
        k = event.keysym
        if k == "Up":
            self._adjust(+1)
        elif k == "Down":
            self._adjust(-1)
        elif k == "Return":
            if self.step < len(self.FIELDS) - 1:
                self.step += 1
                self._refresh()
            else:
                self.app.show_screen("t3")
        elif k == "Left":
            if self.step > 0:
                self.step -= 1
                self._refresh()
            else:
                self.app.show_screen("t1")


# ============================================================================
# T3 — REVISÃO + FEED DA CÂMERA
# ============================================================================

class ScreenT3(BaseScreen):
    """
    Mostra resumo dos parâmetros + feed ao vivo.
    ← →  seleciona botão (VOLTAR / INICIAR)
    ENTER confirma o botão selecionado.
    """

    def __init__(self, app):
        super().__init__(app)
        self.sel = 1  # 0 = VOLTAR, 1 = INICIAR (padrão)
        self._build()
        self._style_buttons()
        if CV2_AVAILABLE:
            self._update_feed()

    def _build(self):
        # Título
        ctk.CTkLabel(
            self, text="PRONTO PARA INICIAR",
            font=ctk.CTkFont(size=24, weight="bold"), text_color=C["white"],
        ).pack(pady=(20, 12))

        # Conteúdo (2 colunas)
        body = ctk.CTkFrame(self, fg_color=C["transparent"])
        body.pack(fill="both", expand=True, padx=30)
        body.grid_columnconfigure(0, weight=1)
        body.grid_columnconfigure(1, weight=1)

        # ---- col esquerda: info ----
        info = ctk.CTkFrame(body, fg_color=C["transparent"])
        info.grid(row=0, column=0, sticky="nsew", padx=(0, 12))

        interval = self.app.total_time / max(self.app.image_number, 1)
        rows = [
            ("Capturas:", str(self.app.image_number)),
            ("Tempo total:", f"{self.app.total_time} s"),
            ("Intervalo:", f"{interval:.1f} s / captura"),
        ]
        for label, value in rows:
            row = ctk.CTkFrame(
                info, fg_color=C["bg_card"], corner_radius=10, height=58,
            )
            row.pack(fill="x", pady=4)
            row.pack_propagate(False)
            ctk.CTkLabel(
                row, text=label, font=ctk.CTkFont(size=14),
                text_color=C["text2"],
            ).place(relx=0.06, rely=0.5, anchor="w")
            ctk.CTkLabel(
                row, text=value,
                font=ctk.CTkFont(size=20, weight="bold"),
                text_color=C["green"],
            ).place(relx=0.94, rely=0.5, anchor="e")

        # ---- col direita: feed câmera ----
        feed_card = ctk.CTkFrame(
            body, fg_color=C["bg_card"], corner_radius=12,
            border_width=1, border_color=C["border"],
        )
        feed_card.grid(row=0, column=1, sticky="nsew", padx=(12, 0))

        ctk.CTkLabel(
            feed_card, text="CÂMERA", font=ctk.CTkFont(size=11),
            text_color=C["muted"],
        ).place(relx=0.5, rely=0.04, anchor="n")

        # Label tkinter puro (mais rápido p/ atualização de imagem)
        self._cam = tk.Label(
            feed_card, bg=C["bg_card"], bd=0, highlightthickness=0,
        )
        self._cam.place(relx=0.5, rely=0.53, anchor="center",
                        relwidth=0.92, relheight=0.86)

        if not self.app.camera.available:
            self._cam.configure(text="📷  Câmera não disponível",
                                fg=C["muted"], font=("Segoe UI", 11))

        # ---- botões ----
        btn_bar = ctk.CTkFrame(self, fg_color=C["transparent"], height=60)
        btn_bar.pack(fill="x", padx=30, pady=(8, 4))
        btn_bar.pack_propagate(False)
        btn_bar.grid_columnconfigure(0, weight=1)
        btn_bar.grid_columnconfigure(1, weight=1)

        self._btn_v = ctk.CTkButton(
            btn_bar, text="← VOLTAR",
            font=ctk.CTkFont(size=15, weight="bold"),
            corner_radius=10, height=46,
        )
        self._btn_v.grid(row=0, column=0, padx=(0, 8), sticky="ew")

        self._btn_i = ctk.CTkButton(
            btn_bar, text="INICIAR →",
            font=ctk.CTkFont(size=15, weight="bold"),
            corner_radius=10, height=46,
        )
        self._btn_i.grid(row=0, column=1, padx=(8, 0), sticky="ew")

        # dica
        ctk.CTkLabel(
            self, text="← →  Selecionar      ENTER  Confirmar",
            font=ctk.CTkFont(size=11), text_color=C["muted"],
        ).pack(pady=(0, 10))

    # --- estilo dos botões ---

    def _style_buttons(self):
        if self.sel == 1:  # INICIAR ativo
            self._btn_i.configure(
                fg_color=C["green"], hover_color=C["green_dark"],
                text_color=C["black"], border_width=0,
            )
            self._btn_v.configure(
                fg_color=C["btn_off"], hover_color=C["btn_off"],
                text_color=C["text2"], border_width=1,
                border_color=C["btn_off_border"],
            )
        else:  # VOLTAR ativo
            self._btn_v.configure(
                fg_color=C["green"], hover_color=C["green_dark"],
                text_color=C["black"], border_width=0,
            )
            self._btn_i.configure(
                fg_color=C["btn_off"], hover_color=C["btn_off"],
                text_color=C["text2"], border_width=1,
                border_color=C["btn_off_border"],
            )

    # --- feed ao vivo ---

    def _update_feed(self):
        if not self.winfo_exists():
            return
        frame = self.app.camera.get_frame()
        if frame is not None:
            w = max(self._cam.winfo_width(), 200)
            h = max(self._cam.winfo_height(), 150)
            if w > 1 and h > 1:
                rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                rgb = cv2.resize(rgb, (w, h))
                photo = ImageTk.PhotoImage(Image.fromarray(rgb))
                self._cam.configure(image=photo, text="")
                self._cam.image = photo  # manter referência
        self.safe_after(50, self._update_feed)

    # --- teclado ---

    def handle_key(self, event):
        k = event.keysym
        if k == "Left":
            self.sel = 0
            self._style_buttons()
        elif k == "Right":
            self.sel = 1
            self._style_buttons()
        elif k == "Return":
            if self.sel == 0:
                self.app.show_screen("t2")
            else:
                self.app.start_exam()


# ============================================================================
# T4 — CAPTURANDO  (exame em andamento — botões bloqueados)
# ============================================================================

class ScreenT4(BaseScreen):

    def __init__(self, app):
        super().__init__(app)
        self.total_cap = app.image_number
        self.total_sec = app.total_time
        self.interval = self.total_sec / max(self.total_cap, 1)
        self.captured = 0
        self.start_time = None
        self.last_cap_time = 0
        self.dot_on = True
        self.active = True
        self._build()

    def _build(self):
        # ---- header ----
        hdr = ctk.CTkFrame(self, fg_color=C["transparent"], height=55)
        hdr.pack(fill="x", padx=30, pady=(15, 8))
        hdr.pack_propagate(False)

        left = ctk.CTkFrame(hdr, fg_color=C["transparent"])
        left.pack(side="left")

        self._dot = ctk.CTkLabel(
            left, text="●", font=ctk.CTkFont(size=24),
            text_color=C["red"],
        )
        self._dot.pack(side="left", padx=(0, 8))

        ctk.CTkLabel(
            left, text="CAPTURANDO...",
            font=ctk.CTkFont(size=22, weight="bold"), text_color=C["white"],
        ).pack(side="left")

        self._lbl_counter = ctk.CTkLabel(
            hdr, text=f"0 / {self.total_cap}",
            font=ctk.CTkFont(size=32, weight="bold"), text_color=C["green"],
        )
        self._lbl_counter.pack(side="right")

        # ---- body (2 cols) ----
        body = ctk.CTkFrame(self, fg_color=C["transparent"])
        body.pack(fill="both", expand=True, padx=30, pady=(0, 8))
        body.grid_columnconfigure(0, weight=3)
        body.grid_columnconfigure(1, weight=2)

        # -- progresso (esquerda) --
        prog_card = ctk.CTkFrame(
            body, fg_color=C["bg_card"], corner_radius=12,
            border_width=1, border_color=C["border"],
        )
        prog_card.grid(row=0, column=0, sticky="nsew", padx=(0, 12))

        # Capturas
        cf = ctk.CTkFrame(prog_card, fg_color=C["transparent"])
        cf.pack(fill="x", padx=20, pady=(22, 8))
        ch = ctk.CTkFrame(cf, fg_color=C["transparent"])
        ch.pack(fill="x")
        ctk.CTkLabel(
            ch, text="Capturas", font=ctk.CTkFont(size=14),
            text_color=C["text2"],
        ).pack(side="left")
        self._lbl_cap = ctk.CTkLabel(
            ch, text=f"0 de {self.total_cap}",
            font=ctk.CTkFont(size=14), text_color=C["text2"],
        )
        self._lbl_cap.pack(side="right")
        self._bar_cap = ctk.CTkProgressBar(
            cf, progress_color=C["green"], fg_color=C["bg_card_light"],
            height=18, corner_radius=9,
        )
        self._bar_cap.pack(fill="x", pady=(6, 0))
        self._bar_cap.set(0)

        # Tempo
        tf = ctk.CTkFrame(prog_card, fg_color=C["transparent"])
        tf.pack(fill="x", padx=20, pady=(16, 8))
        th = ctk.CTkFrame(tf, fg_color=C["transparent"])
        th.pack(fill="x")
        ctk.CTkLabel(
            th, text="Tempo", font=ctk.CTkFont(size=14),
            text_color=C["text2"],
        ).pack(side="left")
        self._lbl_time = ctk.CTkLabel(
            th, text=f"0.0 s / {self.total_sec} s",
            font=ctk.CTkFont(size=14), text_color=C["text2"],
        )
        self._lbl_time.pack(side="right")
        self._bar_time = ctk.CTkProgressBar(
            tf, progress_color=C["green"], fg_color=C["bg_card_light"],
            height=18, corner_radius=9,
        )
        self._bar_time.pack(fill="x", pady=(6, 0))
        self._bar_time.set(0)

        # Próxima captura
        self._lbl_next = ctk.CTkLabel(
            prog_card, text="Próxima captura em: --",
            font=ctk.CTkFont(size=13), text_color=C["amber"],
        )
        self._lbl_next.pack(padx=20, pady=(12, 18), anchor="w")

        # -- feed (direita) --
        feed = ctk.CTkFrame(
            body, fg_color=C["bg_card"], corner_radius=12,
            border_width=1, border_color=C["border"],
        )
        feed.grid(row=0, column=1, sticky="nsew", padx=(12, 0))

        ctk.CTkLabel(
            feed, text="feed ao vivo",
            font=ctk.CTkFont(size=10), text_color=C["muted"],
        ).place(relx=0.5, rely=0.04, anchor="n")

        self._cam = tk.Label(feed, bg=C["bg_card"], bd=0, highlightthickness=0)
        self._cam.place(relx=0.5, rely=0.53, anchor="center",
                        relwidth=0.92, relheight=0.86)

        # ---- footer ----
        foot = ctk.CTkFrame(
            self, fg_color=C["bg_card_light"], corner_radius=8, height=35,
        )
        foot.pack(fill="x", padx=30, pady=(4, 10))
        foot.pack_propagate(False)
        ctk.CTkLabel(
            foot, text="Aguarde... captura automática em andamento",
            font=ctk.CTkFont(size=12), text_color=C["muted"],
        ).place(relx=0.5, rely=0.5, anchor="center")

    # --- controle da captura ---

    def start_capture(self):
        self.start_time = time.time()
        self.last_cap_time = self.start_time
        self._pulse()
        self._tick()

    def _pulse(self):
        if not self.active or not self.winfo_exists():
            return
        self.dot_on = not self.dot_on
        self._dot.configure(
            text_color=C["red"] if self.dot_on else C["bg"]
        )
        self.safe_after(500, self._pulse)

    def _tick(self):
        if not self.active or not self.winfo_exists():
            return

        now = time.time()
        elapsed = now - self.start_time

        # progresso
        self._bar_cap.set(self.captured / self.total_cap)
        self._bar_time.set(min(elapsed / self.total_sec, 1.0))
        self._lbl_cap.configure(text=f"{self.captured} de {self.total_cap}")
        self._lbl_time.configure(text=f"{elapsed:.1f} s / {self.total_sec} s")
        self._lbl_counter.configure(text=f"{self.captured} / {self.total_cap}")

        # capturar?
        if (now - self.last_cap_time) >= self.interval \
                and self.captured < self.total_cap:
            self._snap(now)

        # countdown
        if self.captured < self.total_cap:
            nxt = self.interval - (now - self.last_cap_time)
            self._lbl_next.configure(
                text=f"Próxima captura em: {max(0, nxt):.1f} s"
            )

        # feed
        self._draw_feed()

        # concluído?
        if self.captured >= self.total_cap:
            self.active = False
            self._lbl_next.configure(
                text="✓ Captura finalizada!", text_color=C["green"],
            )
            self.safe_after(1200, lambda: self.app.show_screen("t5"))
            return

        self.safe_after(50, self._tick)

    def _snap(self, now):
        frame = self.app.camera.get_frame()
        if frame is not None:
            self.captured += 1
            fname = f"{self.app.session_ts}_capture_{self.captured}.jpg"
            fpath = os.path.join(self.app.capture_folder, fname)
            cv2.imwrite(fpath, frame)
            self.app.captured_images.append((fpath, fname))
            self.last_cap_time = now
            print(f" {self.captured}/{self.total_cap}  →  {fpath}")

    def _draw_feed(self):
        if not CV2_AVAILABLE:
            return
        frame = self.app.camera.get_frame()
        if frame is None:
            return
        w = max(self._cam.winfo_width(), 140)
        h = max(self._cam.winfo_height(), 100)
        if w > 1 and h > 1:
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            rgb = cv2.resize(rgb, (w, h))
            photo = ImageTk.PhotoImage(Image.fromarray(rgb))
            self._cam.configure(image=photo, text="")
            self._cam.image = photo

    # bloqueio total de teclas
    def handle_key(self, event):
        pass

    def cleanup(self):
        self.active = False
        super().cleanup()


# ============================================================================
# T5 — EXAME CONCLUÍDO
# ============================================================================

class ScreenT5(BaseScreen):

    def __init__(self, app):
        super().__init__(app)
        self._build()
        self._start_analysis()

    def _build(self):
        box = ctk.CTkFrame(self, fg_color=C["transparent"])
        box.place(relx=0.5, rely=0.45, anchor="center")

        # ✓ ícone
        ring = ctk.CTkFrame(
            box, width=86, height=86, corner_radius=43,
            fg_color=C["transparent"],
            border_width=4, border_color=C["green"],
        )
        ring.pack(pady=(0, 18))
        ring.pack_propagate(False)
        ctk.CTkLabel(
            ring, text="✓", font=ctk.CTkFont(size=40, weight="bold"),
            text_color=C["green"],
        ).place(relx=0.5, rely=0.48, anchor="center")

        # título
        ctk.CTkLabel(
            box, text="EXAME CONCLUÍDO",
            font=ctk.CTkFont(size=28, weight="bold"), text_color=C["white"],
        ).pack(pady=(0, 10))

        # contagem
        n = len(self.app.captured_images)
        ctk.CTkLabel(
            box, text=f"{n} imagens salvas com sucesso",
            font=ctk.CTkFont(size=16), text_color=C["green"],
        ).pack(pady=(0, 6))

        # pasta
        folder = os.path.abspath(self.app.capture_folder)
        ctk.CTkLabel(
            box, text=f"Pasta: {folder}",
            font=ctk.CTkFont(size=12), text_color=C["text2"],
        ).pack(pady=(0, 18))

        # divisor
        ctk.CTkFrame(
            box, height=1, fg_color=C["border"],
        ).pack(fill="x", padx=30, pady=(0, 18))

        # aviso
        ctk.CTkLabel(
            box, text="Retire o aparelho do paciente",
            font=ctk.CTkFont(size=16), text_color=C["amber"],
        ).pack(pady=(0, 28))

        # botão
        ctk.CTkButton(
            box, text="NOVO EXAME",
            font=ctk.CTkFont(size=16, weight="bold"),
            fg_color=C["green"], hover_color=C["green_dark"],
            text_color=C["black"], corner_radius=20,
            width=190, height=44, state="disabled",
        ).pack(pady=(0, 8))

        ctk.CTkLabel(
            box, text="[ ENTER ]",
            font=ctk.CTkFont(size=11), text_color=C["muted"],
        ).pack()

    # --- análise YOLO em background ---

    def _start_analysis(self):
        if not YOLO_AVAILABLE or self.app.model is None:
            return
        if not self.app.captured_images:
            return
        threading.Thread(target=self._analyze, daemon=True).start()

    def _analyze(self):
        imgs = self.app.captured_images
        print(f"\n--- Análise YOLO: {len(imgs)} imagens ---")
        for fpath, fname in imgs:
            try:
                t0 = time.time()
                results = self.app.model.predict(
                    fpath, device="cpu", verbose=False,
                )
                result = results[0]
                out = os.path.join(
                    self.app.analyzed_folder, f"analyzed_{fname}",
                )
                cv2.imwrite(out, result.plot())
                dt = time.time() - t0

                if len(result.boxes) == 0:
                    print(f"  {fname}: nenhuma detecção  ({dt:.2f}s)")
                else:
                    for b in result.boxes:
                        lbl = self.app.model.names[int(b.cls[0])]
                        conf = float(b.conf[0])
                        print(
                            f"  {fname}: {lbl.upper()} "
                            f"({conf*100:.1f}%)  ({dt:.2f}s)"
                        )
            except Exception as e:
                print(f"  ERRO {fname}: {e}")
        print("--- Análise concluída. ---\n")

    def handle_key(self, event):
        if event.keysym == "Return":
            self.app.new_exam()


# ============================================================================
# APLICAÇÃO PRINCIPAL
# ============================================================================

class VisualDetectApp(ctk.CTk):

    def __init__(self, fullscreen=False):
        super().__init__()

        # janela
        self.title("VisualDetect — Triagem do Reflexo Ocular")
        self.geometry(f"{SCREEN_WIDTH}x{SCREEN_HEIGHT}")
        self.configure(fg_color=C["bg"])
        self.resizable(False, False)
        if fullscreen:
            self.attributes("-fullscreen", True)

        # estado
        self.image_number = 10
        self.total_time = 10
        self.current_screen: BaseScreen | None = None
        self.session_ts = ""
        self.captured_images: list[tuple[str, str]] = []

        # pastas
        self.capture_folder = CAPTURE_FOLDER
        self.analyzed_folder = ANALYZED_FOLDER
        os.makedirs(self.capture_folder, exist_ok=True)
        os.makedirs(self.analyzed_folder, exist_ok=True)

        # câmera
        self.camera = CameraManager()
        self.camera.start()

        # modelo YOLO
        self.model = None
        self._load_model()

        # teclado
        self.bind("<KeyPress>", self._on_key)
        self.bind("<Escape>", self._on_esc)
        self.bind("<F11>", self._toggle_fs)

        # cleanup
        self.protocol("WM_DELETE_WINDOW", self._quit)

        # tela inicial
        self.show_screen("t0")

    # --- modelo ---

    def _load_model(self):
        if not YOLO_AVAILABLE:
            return
        try:
            if os.path.exists(MODELO_PATH):
                self.model = YOLO(MODELO_PATH)
                print(f"[OK] Modelo YOLO: {MODELO_PATH}")
            else:
                print(f"[AVISO] Modelo não encontrado: {MODELO_PATH}")
        except Exception as e:
            print(f"[ERRO] Modelo: {e}")

    # --- navegação entre telas ---

    SCREENS = {
        "t0": ScreenT0,
        "t1": ScreenT1,
        "t2": ScreenT2,
        "t3": ScreenT3,
        "t4": ScreenT4,
        "t5": ScreenT5,
    }

    def show_screen(self, name):
        if self.current_screen:
            self.current_screen.cleanup()
            self.current_screen.destroy()
        cls = self.SCREENS.get(name)
        if cls:
            self.current_screen = cls(self)
            self.current_screen.pack(fill="both", expand=True)
            self.focus_force()
            if name == "t4":
                self.current_screen.start_capture()

    def start_exam(self):
        self.session_ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.captured_images = []
        self.show_screen("t4")

    def new_exam(self):
        self.captured_images = []
        self.show_screen("t1")

    # --- teclado ---

    def _on_key(self, event):
        if self.current_screen:
            self.current_screen.handle_key(event)

    def _on_esc(self, _):
        if self.attributes("-fullscreen"):
            self.attributes("-fullscreen", False)
        else:
            self._quit()

    def _toggle_fs(self, _=None):
        self.attributes("-fullscreen", not self.attributes("-fullscreen"))

    # --- saída limpa ---

    def _quit(self):
        if self.current_screen:
            self.current_screen.cleanup()
        self.camera.stop()
        self.destroy()


# ============================================================================
# PONTO DE ENTRADA
# ============================================================================

def main():
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("dark-blue")

    fs = "--fullscreen" in sys.argv or "-f" in sys.argv

    print("=" * 50)
    print("  VISUAL DETECT — Interface Gráfica")
    print("  Equipamento de Triagem do Reflexo Ocular")
    print("=" * 50)
    print(f"  Resolução: {SCREEN_WIDTH}×{SCREEN_HEIGHT}")
    print(f"  Fullscreen: {'Sim' if fs else 'Não (use --fullscreen)'}")
    print(f"  Câmera: {'disponível' if CV2_AVAILABLE else 'indisponível'}")
    print(f"  YOLO: {'disponível' if YOLO_AVAILABLE else 'indisponível'}")
    print("=" * 50)

    app = VisualDetectApp(fullscreen=fs)
    app.mainloop()


if __name__ == "__main__":
    main()
