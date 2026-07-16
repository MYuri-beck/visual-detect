"""
main.py — Ponto de entrada do VisualDetect
==========================================
Instancia o backend (camera + modelo + sessao) e entrega tudo
para a UI via injecao de dependencia. Nenhuma logica de negocio vive aqui.

Para rodar:
  python main.py              # janela 800x480
  python main.py --fullscreen # tela cheia (Raspberry Pi)
"""

import os
import sys
import customtkinter as ctk

from backend import CameraManager, VisionAnalyzer, CaptureSession


# ============================================================================
# CONFIGURACAO — ajuste aqui antes de rodar no Raspberry Pi
# ============================================================================

# Diretorio da pasta app/ — tudo fica aqui dentro para facilitar o deploy
# no Raspberry Pi: copie apenas a pasta app/ e ela ja funciona sozinha.
_APP_DIR = os.path.dirname(os.path.abspath(__file__))

# Caminho para o modelo YOLO treinado.
# PARA ALTERAR o modelo: substitua 'best.pt' pelo nome do seu arquivo .pt
# Coloque o arquivo em: app/models/best.pt
MODELO_PATH = os.path.join(_APP_DIR, "models", "best.pt")

# Pasta onde as imagens brutas capturadas sao salvas
# PARA ALTERAR: mude o nome da pasta (fica sempre dentro de app/)
CAPTURE_FOLDER = os.path.join(_APP_DIR, "capturas_voluntarios_analisar")

# Pasta onde as imagens com anotacoes YOLO sao salvas apos a analise
# PARA ALTERAR: mude o nome da pasta
ANALYZED_FOLDER = os.path.join(_APP_DIR, "capturas_analisadas_voluntarios")


# ============================================================================
# INICIALIZACAO
# ============================================================================

def main():
    print("=" * 50)
    print("  VISUAL DETECT")
    print("  Equipamento de Triagem do Reflexo Ocular")
    print("=" * 50)
    print(f"  Modelo : {os.path.abspath(MODELO_PATH)}")
    print(f"  Capturas: {CAPTURE_FOLDER}")
    print(f"  Analise : {ANALYZED_FOLDER}")
    print("=" * 50)

    # 1. Camera em thread separada
    camera = CameraManager()
    camera.start()

    # 2. Analisador YOLO (o carregamento real ocorre na tela de loading)
    analyzer = VisionAnalyzer(model_path=MODELO_PATH)

    # 3. Sessao de captura, recebendo as pastas configuradas acima
    session = CaptureSession(
        camera=camera,
        analyzer=analyzer,
        capture_folder=CAPTURE_FOLDER,
        analyzed_folder=ANALYZED_FOLDER,
    )

    # 4. Tema visual do customtkinter
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("dark-blue")

    # Importacao da UI aqui (dentro de main) para garantir que o ctk
    # ja esteja configurado antes de qualquer widget ser criado
    from ui import VisualDetectUI

    # 5. Interface grafica com a sessao injetada
    app = VisualDetectUI(backend_session=session)

    # Fullscreen se passado como argumento de linha de comando
    if "--fullscreen" in sys.argv or "-f" in sys.argv:
        app.attributes("-fullscreen", True)

    # 6. Loop principal do tkinter
    app.mainloop()

    # 7. Encerramento limpo — para a thread da camera
    print("Encerrando...")
    camera.stop()


if __name__ == "__main__":
    main()
