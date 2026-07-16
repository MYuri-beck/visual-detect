"""
ui.py — Interface Grafica do VisualDetect (camada de apresentacao)
===================================================================
Cada tela recebe a sessao do backend via injecao de dependencia — nenhuma
logica de camera ou YOLO vive aqui, tudo e delegado ao CaptureSession.

Telas:
  Loading  Carregando modelo YOLO (avanca sozinha ao terminar)
  T0       Info SENAI/NUDEP
  T1       Splash VisualDetect
  T2       Configuracao (wizard — um campo por vez)
  T3       Revisao + Feed da camera
  T4       Capturando (automatico, botoes bloqueados)
  T5       Exame concluido

Navegacao via ESP32 HID (<- -> up down ENTER) ou teclado comum.
"""

import os
import time
import tkinter as tk

import customtkinter as ctk

# cv2 e PIL sao opcionais — o feed de camera e desabilitado se nao estiverem
try:
    import cv2
    from PIL import Image, ImageTk
    _CV2_OK = True
except ImportError:
    _CV2_OK = False


# ============================================================================
# CONFIGURACAO VISUAL
# ============================================================================
# PARA ALTERAR a resolucao da janela: mude SCREEN_WIDTH e SCREEN_HEIGHT
SCREEN_WIDTH  = 800
SCREEN_HEIGHT = 480

# Paleta de cores da aplicacao (roxo escuro + verde + ambar)
# PARA ALTERAR qualquer cor: mude o valor hex correspondente
C = {
    "bg":             "#0d0b1a",
    "bg_card":        "#1a1533",
    "bg_card_light":  "#252040",
    "bg_field":       "#1e1940",
    "border":         "#2d2755",
    "border_active":  "#00e676",
    "green":          "#00e676",
    "green_dark":     "#00c853",
    "white":          "#ffffff",
    "text2":          "#9e9ab8",
    "muted":          "#5c5880",
    "amber":          "#ffc107",
    "red":            "#ff1744",
    "purple":         "#7c4dff",
    "purple_light":   "#b388ff",
    "btn_off":        "#2a2550",
    "btn_off_border": "#3d3670",
    "black":          "#000000",
    "transparent":    "transparent",
}


# ============================================================================
# CLASSE BASE
# ============================================================================

class BaseScreen(ctk.CTkFrame):
    """Todas as telas herdam daqui para ter after() seguro e handle_key."""

    def __init__(self, app, **kw):
        kw.setdefault("fg_color", C["bg"])
        super().__init__(app, **kw)
        self.app = app
        # session é o CaptureSession injetado pelo VisualDetectUI
        self.session = app.session
        self._after_ids: list = []

    def safe_after(self, ms, callback):
        """Registra o after() para que seja cancelado ao trocar de tela."""
        aid = self.after(ms, callback)
        self._after_ids.append(aid)
        return aid

    def cleanup(self):
        """Cancela todos os after() pendentes desta tela."""
        for aid in self._after_ids:
            try:
                self.after_cancel(aid)
            except Exception:
                pass
        self._after_ids.clear()

    def handle_key(self, event):
        """Sobrescrever nas subclasses para tratar input de teclado/HID."""
        pass

    @staticmethod
    def _load_ctk_image(path, max_w, max_h):
        """
        Carrega um PNG (com ou sem transparencia) como CTkImage.
        Retorna None se o arquivo nao existir ou ocorrer erro.

        PARA ALTERAR o tamanho maximo das logos: passe max_w e max_h diferentes
        ao chamar este metodo nas telas individuais.
        """
        try:
            img = Image.open(path).convert("RGBA")
            img.thumbnail((max_w, max_h), Image.LANCZOS)
            return ctk.CTkImage(light_image=img, dark_image=img,
                                size=(img.width, img.height))
        except Exception as e:
            print(f"[AVISO] Imagem nao carregada ({path}): {e}")
            return None


# ============================================================================
# LOADING — carrega modelo YOLO sem travar a janela
# ============================================================================

class ScreenLoading(BaseScreen):
    """
    Exibida durante o carregamento do modelo YOLO.
    Quando o backend sinaliza que terminou, avanca automaticamente para T0.
    """

    def __init__(self, app):
        super().__init__(app)
        self._dot_count = 0
        self._build()
        self._animate()

        # Dispara o carregamento do modelo em background e pede callback quando pronto
        self.session.analyzer.load_async(
            on_ready=lambda: self.after(0, self._on_model_ready)
        )

    def _build(self):
        box = ctk.CTkFrame(self, fg_color=C["transparent"])
        box.place(relx=0.5, rely=0.5, anchor="center")

        # Titulo principal sem emoji — compativel com fontes de sistema do Raspberry Pi
        ctk.CTkLabel(
            box, text="VISUAL DETECT",
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color=C["white"],
        ).pack(pady=(0, 6))

        ctk.CTkLabel(
            box, text="Equipamento de Triagem do Reflexo Ocular",
            font=ctk.CTkFont(size=13), text_color=C["text2"],
        ).pack(pady=(0, 30))

        # Barra de progresso no modo indeterminado (animacao automatica)
        self._progress = ctk.CTkProgressBar(
            box, mode="indeterminate",
            progress_color=C["green"], fg_color=C["bg_card_light"],
            width=260, height=8, corner_radius=4,
        )
        self._progress.pack(pady=(0, 14))
        self._progress.start()

        self._lbl_status = ctk.CTkLabel(
            box, text="Inicializando...",
            font=ctk.CTkFont(size=12), text_color=C["muted"],
        )
        self._lbl_status.pack()

    def _animate(self):
        """Atualiza o texto de status com pontinhos animados enquanto carrega."""
        if not self.winfo_exists():
            return
        dots = "." * (self._dot_count % 4)
        self._lbl_status.configure(text=f"Carregando modelo{dots}")
        self._dot_count += 1
        self.safe_after(400, self._animate)

    def _on_model_ready(self):
        """Chamado pela thread do backend via after(0) quando o modelo esta pronto."""
        if not self.winfo_exists():
            return
        self._progress.stop()
        self._lbl_status.configure(text="Pronto!", text_color=C["green"])
        # Pausa breve para o usuario ver o "Pronto!" antes de avancar
        self.safe_after(600, lambda: self.app.show_screen("t0"))


# ============================================================================
# T0 — INFORMACOES INSTITUCIONAIS
# ============================================================================

class ScreenT0(BaseScreen):

    def __init__(self, app):
        super().__init__(app)
        self._build()

    def _build(self):
        box = ctk.CTkFrame(self, fg_color=C["transparent"])
        box.place(relx=0.5, rely=0.5, anchor="center")

        # Caminho para a logo NUDEP — dentro de app/assets/
        _nudep_png = os.path.join(
            os.path.dirname(__file__),
            "assets", "logo - NUDEP_branco_png.png",
        )
        # PARA ALTERAR o tamanho maximo da logo NUDEP: mude os dois numeros abaixo
        img = self._load_ctk_image(_nudep_png, 260, 130)
        if img:
            ctk.CTkLabel(box, image=img, text="").pack(pady=(0, 24))
        else:
            ctk.CTkLabel(box, text="[ SENAI / NUDEP ]",
                         font=ctk.CTkFont(size=18), text_color=C["muted"]).pack(pady=(0, 24))

        ctk.CTkLabel(
            box,
            text="Centro de Formacao Profissional SENAI\nPlinio Gilberto Kroeff",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=C["white"], justify="center",
        ).pack(pady=(0, 10))

        ctk.CTkLabel(
            box, text="Curso Tecnico em Desenvolvimento de Sistemas",
            font=ctk.CTkFont(size=15), text_color=C["text2"], justify="center",
        ).pack(pady=(0, 25))

        ctk.CTkLabel(box, text="Autores:",
                     font=ctk.CTkFont(size=14), text_color=C["green"]).pack(pady=(0, 4))
        ctk.CTkLabel(box, text="Yuri Mendes  |  Andrei Krug",
                     font=ctk.CTkFont(size=16, weight="bold"),
                     text_color=C["white"]).pack(pady=(0, 30))

        ctk.CTkLabel(box, text="Pressione ENTER para continuar",
                     font=ctk.CTkFont(size=12), text_color=C["muted"]).pack()

    def handle_key(self, event):
        if event.keysym == "Return":
            self.app.show_screen("t1")


# ============================================================================
# T1 — SPLASH
# ============================================================================

class ScreenT1(BaseScreen):

    def __init__(self, app):
        super().__init__(app)
        self._build()

    def _build(self):
        # Card central com borda sutil
        card = ctk.CTkFrame(
            self, fg_color=C["bg_card"], corner_radius=16,
            border_width=1, border_color=C["border"],
        )
        card.place(relx=0.5, rely=0.5, anchor="center",
                   relwidth=0.88, relheight=0.88)

        # Versao no canto superior direito
        ctk.CTkLabel(card, text="v1.0", font=ctk.CTkFont(size=11),
                     text_color=C["muted"]).place(relx=0.96, rely=0.05, anchor="ne")

        center = ctk.CTkFrame(card, fg_color=C["transparent"])
        center.place(relx=0.5, rely=0.45, anchor="center")

        # Caminho para a logo VisualDetect — dentro de app/assets/
        _vd_png = os.path.join(
            os.path.dirname(__file__),
            "assets",
            "logo - VisualDetect_greenPupil_png-Photoroom.png",
        )
        # PARA ALTERAR o tamanho maximo da logo VisualDetect: mude os dois numeros abaixo
        img = self._load_ctk_image(_vd_png, 300, 150)
        if img:
            ctk.CTkLabel(center, image=img, text="").pack(pady=(0, 18))
        else:
            # Fallback sem emoji caso a imagem nao seja encontrada
            ctk.CTkLabel(center, text="[ VD ]", font=ctk.CTkFont(size=40),
                         text_color=C["purple"]).pack(pady=(0, 18))

        ctk.CTkLabel(center, text="VISUAL DETECT",
                     font=ctk.CTkFont(size=34, weight="bold"),
                     text_color=C["white"]).pack(pady=(0, 6))

        ctk.CTkLabel(center, text="Equipamento de Triagem do Reflexo Ocular",
                     font=ctk.CTkFont(size=14), text_color=C["text2"]).pack(pady=(0, 28))

        # Botao INICIAR decorativo — a navegacao e feita pelo teclado/HID
        ctk.CTkButton(
            center, text="INICIAR",
            font=ctk.CTkFont(size=16, weight="bold"),
            fg_color=C["green"], hover_color=C["green_dark"],
            text_color=C["black"], corner_radius=20,
            width=170, height=44, state="disabled",
        ).pack(pady=(0, 8))

        ctk.CTkLabel(center, text="[ ENTER ]",
                     font=ctk.CTkFont(size=11), text_color=C["muted"]).pack()

    def handle_key(self, event):
        if event.keysym == "Return":
            self.app.show_screen("t2")


# ============================================================================
# T2 — CONFIGURACAO (wizard)
# ============================================================================

class ScreenT2(BaseScreen):
    """
    Wizard de 2 passos para configurar o exame:
      Passo 0 -> Nr de capturas  (Up/Down ajusta, ENTER avanca, Left volta)
      Passo 1 -> Tempo total      (Up/Down ajusta, ENTER confirma, Left volta)
    Os valores sao salvos direto no session.
    """

    FIELDS = [
        {"label": "Nr DE CAPTURAS", "attr": "image_number", "mn": 1,  "mx": 50,  "unit": ""},
        {"label": "TEMPO TOTAL",    "attr": "total_time",   "mn": 1,  "mx": 120, "unit": " s"},
    ]

    def __init__(self, app):
        super().__init__(app)
        self.step = 0
        self._build()
        self._refresh()

    def _build(self):
        # Header com titulo e indicador de passo
        hdr = ctk.CTkFrame(self, fg_color=C["transparent"], height=50)
        hdr.pack(fill="x", padx=30, pady=(20, 0))
        hdr.pack_propagate(False)

        ctk.CTkLabel(hdr, text="<", font=ctk.CTkFont(size=26, weight="bold"),
                     text_color=C["text2"]).pack(side="left")
        ctk.CTkLabel(hdr, text="CONFIGURACAO DO EXAME",
                     font=ctk.CTkFont(size=18, weight="bold"),
                     text_color=C["white"]).pack(side="left", padx=15)

        self._lbl_step = ctk.CTkLabel(hdr, font=ctk.CTkFont(size=13), text_color=C["muted"])
        self._lbl_step.pack(side="right")

        # Card central com o valor atual e as setas de ajuste
        card = ctk.CTkFrame(
            self, fg_color=C["bg_card"], corner_radius=16,
            border_width=2, border_color=C["border_active"],
        )
        card.place(relx=0.5, rely=0.48, anchor="center",
                   relwidth=0.65, relheight=0.50)

        # Nome do campo atual
        self._lbl_name = ctk.CTkLabel(card, font=ctk.CTkFont(size=16), text_color=C["text2"])
        self._lbl_name.place(relx=0.5, rely=0.15, anchor="center")

        # Seta para cima (visual — a navegacao real e pelo teclado)
        ctk.CTkLabel(card, text="\u2191", font=ctk.CTkFont(size=22),
                     text_color=C["muted"]).place(relx=0.5, rely=0.30, anchor="center")

        # Valor atual em destaque
        # PARA ALTERAR o tamanho da fonte do valor: mude o size abaixo
        self._lbl_val = ctk.CTkLabel(card, font=ctk.CTkFont(size=56, weight="bold"),
                                     text_color=C["white"])
        self._lbl_val.place(relx=0.5, rely=0.52, anchor="center")

        # Seta para baixo (visual)
        ctk.CTkLabel(card, text="\u2193", font=ctk.CTkFont(size=22),
                     text_color=C["muted"]).place(relx=0.5, rely=0.72, anchor="center")

        # Dots de progresso (um por passo do wizard)
        self._dots_frame = ctk.CTkFrame(card, fg_color=C["transparent"])
        self._dots_frame.place(relx=0.5, rely=0.90, anchor="center")
        self._dots = []
        for _ in range(len(self.FIELDS)):
            # PARA ALTERAR o tamanho dos dots: mude width e height abaixo
            d = ctk.CTkFrame(self._dots_frame, width=10, height=10,
                             corner_radius=5, fg_color=C["muted"])
            d.pack(side="left", padx=4)
            self._dots.append(d)

        # Footer com dicas de controle
        foot = ctk.CTkFrame(self, fg_color=C["bg_card_light"], corner_radius=8, height=40)
        foot.pack(side="bottom", fill="x", padx=30, pady=15)
        foot.pack_propagate(False)
        self._lbl_hints = ctk.CTkLabel(foot, font=ctk.CTkFont(size=12), text_color=C["muted"])
        self._lbl_hints.place(relx=0.5, rely=0.5, anchor="center")

    def _refresh(self):
        """Atualiza todos os elementos visuais com base no passo atual."""
        f = self.FIELDS[self.step]
        val = getattr(self.session, f["attr"])
        self._lbl_step.configure(text=f"Passo {self.step + 1} / {len(self.FIELDS)}")
        self._lbl_name.configure(text=f["label"])
        self._lbl_val.configure(text=f"{val}{f['unit']}")

        for i, d in enumerate(self._dots):
            d.configure(fg_color=C["green"] if i == self.step else C["muted"])

        hints = ("↑ ↓  Ajustar      ENTER  Próximo      ←  Voltar"
                 if self.step == 0
                 else "↑ ↓  Ajustar      ENTER  Confirmar    ←  Voltar")
        self._lbl_hints.configure(text=hints)

    def _adjust(self, delta):
        """Incrementa ou decrementa o valor do campo atual dentro dos limites."""
        f = self.FIELDS[self.step]
        cur = getattr(self.session, f["attr"])
        new = max(f["mn"], min(f["mx"], cur + delta))
        setattr(self.session, f["attr"], new)
        self._refresh()
        # Flash verde para dar feedback visual imediato ao usuario
        self._lbl_val.configure(text_color=C["green"])
        self.safe_after(200, lambda: self._lbl_val.configure(text_color=C["white"]))

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
# T3 — REVISAO + FEED DA CAMERA
# ============================================================================

class ScreenT3(BaseScreen):
    """
    Resume os parametros configurados e mostra o feed ao vivo da camera.
    Left/Right seleciona botao (VOLTAR / INICIAR), ENTER confirma.
    """

    def __init__(self, app):
        super().__init__(app)
        self.sel = 1  # 0 = VOLTAR, 1 = INICIAR (padrao)
        self._build()
        self._style_buttons()
        if _CV2_OK:
            self._update_feed()

    def _build(self):
        ctk.CTkLabel(
            self, text="PRONTO PARA INICIAR",
            font=ctk.CTkFont(size=24, weight="bold"), text_color=C["white"],
        ).pack(pady=(20, 12))

        body = ctk.CTkFrame(self, fg_color=C["transparent"])
        body.pack(fill="both", expand=True, padx=30)
        body.grid_columnconfigure(0, weight=1)
        body.grid_columnconfigure(1, weight=1)

        # Coluna esquerda: resumo dos parametros configurados
        info = ctk.CTkFrame(body, fg_color=C["transparent"])
        info.grid(row=0, column=0, sticky="nsew", padx=(0, 12))

        interval = self.session.total_time / max(self.session.image_number, 1)
        rows = [
            ("Capturas:",    str(self.session.image_number)),
            ("Tempo total:", f"{self.session.total_time} s"),
            ("Intervalo:",   f"{interval:.1f} s / captura"),
        ]
        for label, value in rows:
            row = ctk.CTkFrame(info, fg_color=C["bg_card"], corner_radius=10, height=58)
            row.pack(fill="x", pady=4)
            row.pack_propagate(False)
            ctk.CTkLabel(row, text=label, font=ctk.CTkFont(size=14),
                         text_color=C["text2"]).place(relx=0.06, rely=0.5, anchor="w")
            ctk.CTkLabel(row, text=value, font=ctk.CTkFont(size=20, weight="bold"),
                         text_color=C["green"]).place(relx=0.94, rely=0.5, anchor="e")

        # Coluna direita: feed ao vivo da camera
        feed_card = ctk.CTkFrame(body, fg_color=C["bg_card"], corner_radius=12,
                                 border_width=1, border_color=C["border"])
        feed_card.grid(row=0, column=1, sticky="nsew", padx=(12, 0))

        ctk.CTkLabel(feed_card, text="CAMERA", font=ctk.CTkFont(size=11),
                     text_color=C["muted"]).place(relx=0.5, rely=0.04, anchor="n")

        # Label tkinter puro para o frame da camera (mais rapido que CTkLabel para imagens)
        self._cam = tk.Label(feed_card, bg=C["bg_card"], bd=0, highlightthickness=0)
        self._cam.place(relx=0.5, rely=0.53, anchor="center",
                        relwidth=0.92, relheight=0.86)

        if not self.session.camera.available:
            self._cam.configure(text="Camera nao disponivel",
                                fg=C["muted"], font=("Segoe UI", 11))

        # Barra de botoes
        btn_bar = ctk.CTkFrame(self, fg_color=C["transparent"], height=60)
        btn_bar.pack(fill="x", padx=30, pady=(8, 4))
        btn_bar.pack_propagate(False)
        btn_bar.grid_columnconfigure(0, weight=1)
        btn_bar.grid_columnconfigure(1, weight=1)

        # PARA ALTERAR o tamanho dos botoes: mude height= abaixo
        self._btn_v = ctk.CTkButton(btn_bar, text="<- VOLTAR",
                                    font=ctk.CTkFont(size=15, weight="bold"),
                                    corner_radius=10, height=46)
        self._btn_v.grid(row=0, column=0, padx=(0, 8), sticky="ew")

        self._btn_i = ctk.CTkButton(btn_bar, text="INICIAR ->",
                                    font=ctk.CTkFont(size=15, weight="bold"),
                                    corner_radius=10, height=46)
        self._btn_i.grid(row=0, column=1, padx=(8, 0), sticky="ew")

        ctk.CTkLabel(self, text="← →  Selecionar      ENTER  Confirmar",
                     font=ctk.CTkFont(size=11), text_color=C["muted"]).pack(pady=(0, 10))

    def _style_buttons(self):
        """Aplica estilos de ativo/inativo nos botoes conforme a selecao atual."""
        if self.sel == 1:  # INICIAR ativo
            self._btn_i.configure(fg_color=C["green"], hover_color=C["green_dark"],
                                  text_color=C["black"], border_width=0)
            self._btn_v.configure(fg_color=C["btn_off"], hover_color=C["btn_off"],
                                  text_color=C["text2"], border_width=1,
                                  border_color=C["btn_off_border"])
        else:  # VOLTAR ativo
            self._btn_v.configure(fg_color=C["green"], hover_color=C["green_dark"],
                                  text_color=C["black"], border_width=0)
            self._btn_i.configure(fg_color=C["btn_off"], hover_color=C["btn_off"],
                                  text_color=C["text2"], border_width=1,
                                  border_color=C["btn_off_border"])

    def _update_feed(self):
        """Atualiza o label da camera a cada 50ms enquanto a tela existe."""
        if not self.winfo_exists():
            return
        frame = self.session.camera.get_frame()
        if frame is not None:
            w = max(self._cam.winfo_width(), 200)
            h = max(self._cam.winfo_height(), 150)
            if w > 1 and h > 1:
                rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                # Calcula o maior tamanho que caiba no container mantendo o
                # aspect ratio original da camera (evita imagem achatada)
                cam_h, cam_w = rgb.shape[:2]
                scale = min(w / cam_w, h / cam_h)
                new_w = int(cam_w * scale)
                new_h = int(cam_h * scale)
                rgb = cv2.resize(rgb, (new_w, new_h))
                photo = ImageTk.PhotoImage(Image.fromarray(rgb))
                self._cam.configure(image=photo, text="")
                self._cam.image = photo  # manter referencia para evitar garbage collection
        self.safe_after(50, self._update_feed)

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
# T4 — CAPTURANDO
# ============================================================================

class ScreenT4(BaseScreen):
    """Tela exibida durante a captura — botoes bloqueados, progresso em tempo real."""

    def __init__(self, app):
        super().__init__(app)
        # Copia os parametros da sessao para nao depender de leitura dinamica
        self.total_cap  = self.session.image_number
        self.total_sec  = self.session.total_time
        self.interval   = self.total_sec / max(self.total_cap, 1)
        self._captured  = 0
        self._start     = None
        self._last_snap = 0
        self._dot_on    = True
        self._active    = True
        self._build()

    def _build(self):
        # Header: indicador de gravacao + contador de fotos
        hdr = ctk.CTkFrame(self, fg_color=C["transparent"], height=55)
        hdr.pack(fill="x", padx=30, pady=(15, 8))
        hdr.pack_propagate(False)

        left = ctk.CTkFrame(hdr, fg_color=C["transparent"])
        left.pack(side="left")

        # Ponto vermelho piscante que indica captura ativa
        self._dot = ctk.CTkLabel(left, text="*", font=ctk.CTkFont(size=24),
                                 text_color=C["red"])
        self._dot.pack(side="left", padx=(0, 8))

        ctk.CTkLabel(left, text="CAPTURANDO...",
                     font=ctk.CTkFont(size=22, weight="bold"),
                     text_color=C["white"]).pack(side="left")

        # Contador "X / total" no canto direito do header
        # PARA ALTERAR o tamanho do contador: mude size= abaixo
        self._lbl_counter = ctk.CTkLabel(hdr, text=f"0 / {self.total_cap}",
                                         font=ctk.CTkFont(size=32, weight="bold"),
                                         text_color=C["green"])
        self._lbl_counter.pack(side="right")

        # Body: 2 colunas (progresso + feed)
        body = ctk.CTkFrame(self, fg_color=C["transparent"])
        body.pack(fill="both", expand=True, padx=30, pady=(0, 8))
        body.grid_columnconfigure(0, weight=3)
        body.grid_columnconfigure(1, weight=2)

        # Coluna esquerda: barras de progresso
        prog = ctk.CTkFrame(body, fg_color=C["bg_card"], corner_radius=12,
                            border_width=1, border_color=C["border"])
        prog.grid(row=0, column=0, sticky="nsew", padx=(0, 12))

        # Barra de capturas
        cf = ctk.CTkFrame(prog, fg_color=C["transparent"])
        cf.pack(fill="x", padx=20, pady=(22, 8))
        ch = ctk.CTkFrame(cf, fg_color=C["transparent"])
        ch.pack(fill="x")
        ctk.CTkLabel(ch, text="Capturas", font=ctk.CTkFont(size=14),
                     text_color=C["text2"]).pack(side="left")
        self._lbl_cap = ctk.CTkLabel(ch, text=f"0 de {self.total_cap}",
                                     font=ctk.CTkFont(size=14), text_color=C["text2"])
        self._lbl_cap.pack(side="right")
        self._bar_cap = ctk.CTkProgressBar(cf, progress_color=C["green"],
                                           fg_color=C["bg_card_light"],
                                           height=18, corner_radius=9)
        self._bar_cap.pack(fill="x", pady=(6, 0))
        self._bar_cap.set(0)

        # Barra de tempo
        tf = ctk.CTkFrame(prog, fg_color=C["transparent"])
        tf.pack(fill="x", padx=20, pady=(16, 8))
        th = ctk.CTkFrame(tf, fg_color=C["transparent"])
        th.pack(fill="x")
        ctk.CTkLabel(th, text="Tempo", font=ctk.CTkFont(size=14),
                     text_color=C["text2"]).pack(side="left")
        self._lbl_time = ctk.CTkLabel(th, text=f"0.0 s / {self.total_sec} s",
                                      font=ctk.CTkFont(size=14), text_color=C["text2"])
        self._lbl_time.pack(side="right")
        self._bar_time = ctk.CTkProgressBar(tf, progress_color=C["green"],
                                            fg_color=C["bg_card_light"],
                                            height=18, corner_radius=9)
        self._bar_time.pack(fill="x", pady=(6, 0))
        self._bar_time.set(0)

        # Label de countdown para proxima captura
        self._lbl_next = ctk.CTkLabel(prog, text="Proxima captura em: --",
                                      font=ctk.CTkFont(size=13), text_color=C["amber"])
        self._lbl_next.pack(padx=20, pady=(12, 18), anchor="w")

        # Coluna direita: feed ao vivo
        feed = ctk.CTkFrame(body, fg_color=C["bg_card"], corner_radius=12,
                            border_width=1, border_color=C["border"])
        feed.grid(row=0, column=1, sticky="nsew", padx=(12, 0))

        ctk.CTkLabel(feed, text="feed ao vivo", font=ctk.CTkFont(size=10),
                     text_color=C["muted"]).place(relx=0.5, rely=0.04, anchor="n")

        self._cam = tk.Label(feed, bg=C["bg_card"], bd=0, highlightthickness=0)
        self._cam.place(relx=0.5, rely=0.53, anchor="center",
                        relwidth=0.92, relheight=0.86)

        # Footer: mensagem de espera
        foot = ctk.CTkFrame(self, fg_color=C["bg_card_light"], corner_radius=8, height=35)
        foot.pack(fill="x", padx=30, pady=(4, 10))
        foot.pack_propagate(False)
        ctk.CTkLabel(foot, text="Aguarde... captura automatica em andamento",
                     font=ctk.CTkFont(size=12), text_color=C["muted"]).place(
            relx=0.5, rely=0.5, anchor="center")

    def start_capture(self):
        """Chamado pelo VisualDetectUI imediatamente apos exibir esta tela."""
        self._start = time.time()
        self._last_snap = self._start
        self._pulse()
        self._tick()

        # Inicia o backend em background com callbacks para atualizar a UI
        self.session.start_exam(
            on_finish_callback=self._on_finish,
            on_progress_callback=self._on_progress,
        )

    # --- callbacks vindos da thread do backend ---

    def _on_progress(self, captured, total):
        """Chamado pela thread do backend — usa after(0) para tocar na UI com seguranca."""
        self.after(0, lambda: self._sync_progress(captured, total))

    def _on_finish(self, captured_images):
        """Chamado pela thread do backend quando todas as fotos foram tiradas e analisadas."""
        self.after(0, lambda: self._finalize())

    def _sync_progress(self, captured, total):
        """Atualiza os labels e a barra de capturas com os valores vindos do backend."""
        if not self.winfo_exists():
            return
        self._captured = captured
        self._lbl_cap.configure(text=f"{captured} de {total}")
        self._lbl_counter.configure(text=f"{captured} / {total}")
        self._bar_cap.set(captured / total)

    def _finalize(self):
        """Exibe a mensagem de conclusao e navega para T5 apos um breve delay."""
        if not self.winfo_exists():
            return
        self._active = False
        self._lbl_next.configure(text="Captura finalizada!", text_color=C["green"])
        self.safe_after(1200, lambda: self.app.show_screen("t5"))

    # --- animacao e tick local de tempo ---

    def _pulse(self):
        """Faz o ponto vermelho piscar alternando entre vermelho e fundo."""
        if not self._active or not self.winfo_exists():
            return
        self._dot_on = not self._dot_on
        self._dot.configure(text_color=C["red"] if self._dot_on else C["bg"])
        self.safe_after(500, self._pulse)

    def _tick(self):
        """Atualiza a barra de tempo e o countdown a cada 50ms."""
        if not self._active or not self.winfo_exists():
            return
        now     = time.time()
        elapsed = now - self._start

        self._bar_time.set(min(elapsed / self.total_sec, 1.0))
        self._lbl_time.configure(text=f"{elapsed:.1f} s / {self.total_sec} s")

        # Countdown para a proxima foto (ressincroniza com o backend via _last_snap)
        since_last = now - self._last_snap
        if self._captured < self.total_cap:
            nxt = self.interval - since_last
            self._lbl_next.configure(text=f"Proxima captura em: {max(0, nxt):.1f} s")
            if since_last >= self.interval:
                self._last_snap = now  # ressincroniza o contador local

        self._draw_feed()
        self.safe_after(50, self._tick)

    def _draw_feed(self):
        """Renderiza o frame mais recente da camera no label de feed."""
        if not _CV2_OK:
            return
        frame = self.session.camera.get_frame()
        if frame is None:
            return
        w = max(self._cam.winfo_width(), 140)
        h = max(self._cam.winfo_height(), 100)
        if w > 1 and h > 1:
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            # Calcula o maior tamanho que caiba no container mantendo o
            # aspect ratio original da camera (evita imagem achatada)
            cam_h, cam_w = rgb.shape[:2]
            scale = min(w / cam_w, h / cam_h)
            new_w = int(cam_w * scale)
            new_h = int(cam_h * scale)
            rgb   = cv2.resize(rgb, (new_w, new_h))
            photo = ImageTk.PhotoImage(Image.fromarray(rgb))
            self._cam.configure(image=photo, text="")
            self._cam.image = photo  # mantém referencia para evitar garbage collection

    # Teclas bloqueadas durante a captura — o usuario nao pode interromper
    def handle_key(self, event):
        pass

    def cleanup(self):
        self._active = False
        super().cleanup()


# ============================================================================
# T5 — EXAME CONCLUIDO
# ============================================================================

class ScreenT5(BaseScreen):

    def __init__(self, app):
        super().__init__(app)
        self._build()

    def _build(self):
        box = ctk.CTkFrame(self, fg_color=C["transparent"])
        box.place(relx=0.5, rely=0.45, anchor="center")

        # Icone de check em circulo
        # PARA ALTERAR o tamanho do icone: mude width, height e corner_radius (metade do tamanho)
        ring = ctk.CTkFrame(box, width=86, height=86, corner_radius=43,
                            fg_color=C["transparent"],
                            border_width=4, border_color=C["green"])
        ring.pack(pady=(0, 18))
        ring.pack_propagate(False)
        ctk.CTkLabel(ring, text="v", font=ctk.CTkFont(size=40, weight="bold"),
                     text_color=C["green"]).place(relx=0.5, rely=0.48, anchor="center")

        ctk.CTkLabel(box, text="EXAME CONCLUIDO",
                     font=ctk.CTkFont(size=28, weight="bold"),
                     text_color=C["white"]).pack(pady=(0, 10))

        n = len(self.session.captured_images)
        ctk.CTkLabel(box, text=f"{n} imagens salvas com sucesso",
                     font=ctk.CTkFont(size=16), text_color=C["green"]).pack(pady=(0, 6))

        folder = os.path.abspath(self.session.CAPTURE_FOLDER)
        ctk.CTkLabel(box, text=f"Pasta: {folder}",
                     font=ctk.CTkFont(size=12), text_color=C["text2"]).pack(pady=(0, 18))

        # Divisor horizontal
        ctk.CTkFrame(box, height=1, fg_color=C["border"]).pack(fill="x", padx=30, pady=(0, 18))

        ctk.CTkLabel(box, text="Retire o aparelho do paciente",
                     font=ctk.CTkFont(size=16), text_color=C["amber"]).pack(pady=(0, 28))

        # Botao decorativo — a acao real e feita pelo teclado
        ctk.CTkButton(
            box, text="NOVO EXAME",
            font=ctk.CTkFont(size=16, weight="bold"),
            fg_color=C["green"], hover_color=C["green_dark"],
            text_color=C["black"], corner_radius=20,
            width=190, height=44, state="disabled",
        ).pack(pady=(0, 8))

        ctk.CTkLabel(box, text="[ ENTER ]",
                     font=ctk.CTkFont(size=11), text_color=C["muted"]).pack()

    def handle_key(self, event):
        if event.keysym == "Return":
            # Usa new_exam() para limpar o estado antes de voltar ao splash
            self.app.new_exam()


# ============================================================================
# APLICACAO PRINCIPAL
# ============================================================================

class VisualDetectUI(ctk.CTk):
    """
    Janela principal — gerencia apenas a UI.
    Recebe a CaptureSession ja configurada via main.py (injecao de dependencia).
    """

    SCREENS = {
        "loading": ScreenLoading,
        "t0": ScreenT0,
        "t1": ScreenT1,
        "t2": ScreenT2,
        "t3": ScreenT3,
        "t4": ScreenT4,
        "t5": ScreenT5,
    }

    def __init__(self, backend_session):
        super().__init__()
        self.session = backend_session

        # PARA ALTERAR o titulo da janela: mude a string abaixo
        self.title("VisualDetect — Triagem do Reflexo Ocular")

        # PARA ALTERAR a resolucao: mude SCREEN_WIDTH e SCREEN_HEIGHT no topo deste arquivo
        self.geometry(f"{SCREEN_WIDTH}x{SCREEN_HEIGHT}")
        self.configure(fg_color=C["bg"])
        self.resizable(False, False)

        self.current_screen: BaseScreen | None = None

        # Atalhos de teclado globais
        self.bind("<KeyPress>", self._on_key)
        self.bind("<Escape>",   self._on_esc)
        self.bind("<F11>",      self._toggle_fs)

        self.protocol("WM_DELETE_WINDOW", self._quit)

        # Primeira tela: carrega o modelo em background e avanca sozinha quando pronto
        self.show_screen("loading")

    # --- navegacao ---

    def show_screen(self, name: str):
        """Destroi a tela atual e exibe a tela indicada pelo nome."""
        if self.current_screen:
            self.current_screen.cleanup()
            self.current_screen.destroy()
        cls = self.SCREENS.get(name)
        if cls:
            self.current_screen = cls(self)
            self.current_screen.pack(fill="both", expand=True)
            self.focus_force()
            # T4 precisa iniciar a captura logo apos ser exibida
            if name == "t4":
                self.current_screen.start_capture()

    def start_exam(self):
        """Navega para a tela de captura (chamado pela T3 ao confirmar INICIAR)."""
        self.show_screen("t4")

    def new_exam(self):
        """Limpa o estado da sessao e volta para o splash para um novo exame."""
        self.session.captured_images = []
        self.show_screen("t1")

    # --- teclado ---

    def _on_key(self, event):
        if self.current_screen:
            self.current_screen.handle_key(event)

    def _on_esc(self, _):
        """ESC sai do fullscreen se ativo, ou fecha a aplicacao."""
        if self.attributes("-fullscreen"):
            self.attributes("-fullscreen", False)
        else:
            self._quit()

    def _toggle_fs(self, _=None):
        """F11 alterna entre fullscreen e janela."""
        self.attributes("-fullscreen", not self.attributes("-fullscreen"))

    # --- saida limpa ---

    def _quit(self):
        """Para a camera e fecha a janela de forma limpa."""
        if self.current_screen:
            self.current_screen.cleanup()
        self.session.camera.stop()
        self.destroy()
