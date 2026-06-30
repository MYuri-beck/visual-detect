import customtkinter as ctk

class ScreenBase(ctk.CTkFrame):
    """Uma classe base opcional para as telas."""
    def __init__(self, master, backend_session):
        super().__init__(master)
        self.backend_session = backend_session

class ScreenT0(ScreenBase):
    def __init__(self, master, backend_session, switch_screen_callback):
        super().__init__(master, backend_session)
        
        # Exemplo de UI
        label = ctk.CTkLabel(self, text="Tela Inicial - SENAI/NUDEP", font=("Arial", 24))
        label.pack(pady=50)
        
        btn = ctk.CTkButton(self, text="Avançar", command=lambda: switch_screen_callback("T1"))
        btn.pack()

class VisualDetectUI(ctk.CTk):
    """Janela principal que apenas gerencia a UI, sem lógicas pesadas."""
    def __init__(self, backend_session):
        super().__init__()
        self.backend_session = backend_session
        
        self.title("VisualDetect - Triagem")
        self.geometry("800x480")
        
        self.current_screen = None
        self.show_screen("T0")
        
    def show_screen(self, screen_name):
        # Destrói a tela atual se existir
        if self.current_screen is not None:
            self.current_screen.destroy()
            
        # Troca para a nova tela
        if screen_name == "T0":
            self.current_screen = ScreenT0(self, self.backend_session, self.show_screen)
            
        # Empacota a nova tela
        if self.current_screen:
            self.current_screen.pack(fill="both", expand=True)
