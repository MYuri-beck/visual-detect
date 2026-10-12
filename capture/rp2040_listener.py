"""
rp2040_listener.py  –  Listener serial para sincronização com RP2040 Zero
==========================================================================
Roda no RPi 4 em paralelo ao backend.py.
Aguarda eventos do RP2040 via USB Serial e dispara a captura da câmera
no momento certo (quando a tela branca está garantidamente acesa).

Protocolo (vindo do RP2040):
    EVENT:GIF_START:<ciclo>    → GIF iniciou, NÃO capturar
    EVENT:DARK_PAUSE           → Tela escura, NÃO capturar
    EVENT:CAPTURE_READY:<ciclo>→ ★ Tela branca acesa — CAPTURAR AGORA

Uso standalone (teste rápido):
    python rp2040_listener.py

Uso integrado ao backend (import):
    from capture.rp2040_listener import RP2040Listener
    listener = RP2040Listener(port="/dev/ttyACM0", on_capture=minha_funcao)
    listener.start()
    ...
    listener.stop()
"""

import os
import cv2
import time
import threading
import serial
import serial.tools.list_ports
from datetime import datetime


# ──────────────────────────────────────────────────────────────────────────────
# Configuração
# ──────────────────────────────────────────────────────────────────────────────

# Pasta onde as imagens da tela branca são salvas
CAPTURE_FOLDER = "capturas_voluntarios_analisar"

# Câmera (índice OpenCV: 0 = padrão, 1 = USB externa)
CAMERA_INDEX = 0

# Quantidade de fotos por evento CAPTURE_READY
SHOTS_PER_CAPTURE = 5

# Intervalo entre cada foto durante a janela de captura (segundos)
SHOT_INTERVAL = 0.4

# Baud rate (deve bater com Serial.begin() no RP2040 — qualquer valor funciona
# em USB CDC, mas é bom deixar igual para clareza)
BAUD_RATE = 115200


# ──────────────────────────────────────────────────────────────────────────────
# Detecção automática da porta do RP2040
# ──────────────────────────────────────────────────────────────────────────────

def find_rp2040_port() -> str | None:
    """
    Varre as portas seriais disponíveis e retorna a primeira que parece
    ser um RP2040 (Raspberry Pi / Waveshare). Retorna None se não encontrar.
    """
    for port in serial.tools.list_ports.comports():
        desc = (port.description or "").lower()
        mfr  = (port.manufacturer or "").lower()
        if any(k in desc or k in mfr for k in ("rp2040", "pico", "raspberry", "waveshare")):
            return port.device
    return None


# ──────────────────────────────────────────────────────────────────────────────
# Classe principal
# ──────────────────────────────────────────────────────────────────────────────

class RP2040Listener:
    """
    Abre a porta serial do RP2040 e escuta eventos em thread separada.
    Ao receber EVENT:CAPTURE_READY, chama `on_capture(cycle, images)`.

    Parâmetros
    ----------
    port       : porta serial (ex: "/dev/ttyACM0"). None = autodetectar.
    on_capture : callable(cycle: int, images: list[str])
                 Chamado na thread do listener quando a captura termina.
                 `images` é lista de caminhos dos arquivos salvos.
    camera_index : índice OpenCV da câmera.
    """

    def __init__(self, port: str | None = None,
                 on_capture=None,
                 camera_index: int = CAMERA_INDEX):
        self._port         = port
        self._on_capture   = on_capture
        self._cam_index    = camera_index
        self._running      = False
        self._thread       = None
        self._ser          = None
        self._cap          = None
        self._lock         = threading.Lock()
        self._last_frame   = None

    # ── câmera ────────────────────────────────────────────────────────────────

    def _start_camera(self):
        """Abre a câmera em thread de captura contínua."""
        self._cap = cv2.VideoCapture(self._cam_index)
        if not self._cap.isOpened():
            print(f"[listener] AVISO: câmera {self._cam_index} não disponível.")
            self._cap = None
            return
        cam_thread = threading.Thread(target=self._camera_loop, daemon=True)
        cam_thread.start()
        print(f"[listener] Câmera {self._cam_index} aberta.")

    def _camera_loop(self):
        """Captura frames contínuos para ter o mais recente disponível."""
        while self._running and self._cap and self._cap.isOpened():
            ret, frame = self._cap.read()
            if ret:
                frame = cv2.flip(frame, 1)   # espelho horizontal
                with self._lock:
                    self._last_frame = frame
            time.sleep(0.01)  # ~100 fps máx — sem travar a CPU

    def _get_frame(self):
        """Retorna o frame mais recente (thread-safe)."""
        with self._lock:
            return self._last_frame.copy() if self._last_frame is not None else None

    # ── captura ───────────────────────────────────────────────────────────────

    def _do_capture(self, cycle: int):
        """
        Tira SHOTS_PER_CAPTURE fotos espaçadas por SHOT_INTERVAL segundos
        e chama o callback on_capture ao terminar.
        Roda em thread separada para não bloquear a leitura serial.
        """
        os.makedirs(CAPTURE_FOLDER, exist_ok=True)
        ts      = datetime.now().strftime("%Y%m%d_%H%M%S")
        saved   = []

        print(f"[listener] ★ CAPTURE_READY ciclo={cycle} — tirando {SHOTS_PER_CAPTURE} fotos...")

        for i in range(SHOTS_PER_CAPTURE):
            frame = self._get_frame()
            if frame is not None:
                fname = f"rp2040_c{cycle:04d}_s{i+1:02d}_{ts}.jpg"
                fpath = os.path.join(CAPTURE_FOLDER, fname)
                cv2.imwrite(fpath, frame)
                saved.append(fpath)
                print(f"  [{i+1}/{SHOTS_PER_CAPTURE}] salvo: {fpath}")
            time.sleep(SHOT_INTERVAL)

        print(f"[listener] Captura ciclo {cycle} concluída ({len(saved)} imagens).")

        if self._on_capture:
            self._on_capture(cycle, saved)

    # ── serial ────────────────────────────────────────────────────────────────

    def _serial_loop(self):
        """Lê linhas da serial e reage a eventos do RP2040."""
        while self._running:
            try:
                raw = self._ser.readline()   # bloqueia até '\n' ou timeout
                if not raw:
                    continue
                line = raw.decode("utf-8", errors="ignore").strip()
                if not line:
                    continue

                print(f"[rp2040] {line}")

                if not line.startswith("EVENT:"):
                    continue   # linha de debug normal — ignora

                parts = line[6:].split(":")   # remove "EVENT:" e divide
                event = parts[0]
                value = int(parts[1]) if len(parts) > 1 else -1

                if event == "CAPTURE_READY":
                    # Dispara captura em thread separada para não bloquear a leitura
                    t = threading.Thread(
                        target=self._do_capture,
                        args=(value,),
                        daemon=True
                    )
                    t.start()

                elif event == "GIF_START":
                    print(f"[listener] Novo ciclo {value} — aguardando próximo CAPTURE_READY.")

                elif event == "DARK_PAUSE":
                    print("[listener] Tela escura — sem captura.")

            except serial.SerialException as e:
                print(f"[listener] ERRO serial: {e}")
                break
            except Exception as e:
                print(f"[listener] Erro inesperado: {e}")

    # ── controle público ──────────────────────────────────────────────────────

    def start(self, port: str | None = None):
        """
        Inicia o listener. Detecta a porta automaticamente se não informada.
        Retorna True se conectou com sucesso, False caso contrário.
        """
        port = port or self._port or find_rp2040_port()
        if port is None:
            print("[listener] RP2040 não encontrado. Conecte via USB e tente novamente.")
            return False

        try:
            self._ser = serial.Serial(port, BAUD_RATE, timeout=1)
            print(f"[listener] Conectado ao RP2040 em {port} @ {BAUD_RATE} baud.")
        except serial.SerialException as e:
            print(f"[listener] Falha ao abrir {port}: {e}")
            return False

        self._running = True
        self._start_camera()

        self._thread = threading.Thread(target=self._serial_loop, daemon=True)
        self._thread.start()
        return True

    def stop(self):
        """Para o listener e libera recursos."""
        self._running = False
        if self._ser and self._ser.is_open:
            self._ser.close()
        if self._cap and self._cap.isOpened():
            self._cap.release()
        print("[listener] Encerrado.")


# ──────────────────────────────────────────────────────────────────────────────
# Entrada standalone (teste rápido)
# ──────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    def on_capture_done(cycle, images):
        print(f"[callback] Ciclo {cycle}: {len(images)} imagens salvas.")

    listener = RP2040Listener(on_capture=on_capture_done)
    if not listener.start():
        exit(1)

    print("Aguardando eventos do RP2040... (Ctrl+C para sair)")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        pass
    finally:
        listener.stop()
