# 📘 Guia de Estudo e Refatoração: VisualDetect (POO e MVC)

Este guia foi feito para você deixar em uma tela secundária enquanto "põe a mão na massa". O objetivo não é te dar o código pronto, mas sim te guiar pela lógica de **Programação Orientada a Objetos (POO)** e separação de camadas.

---

## 🧠 Conceitos Básicos de POO para o Projeto

Antes de mover as linhas, tenha em mente como pensamos em POO:

1. **Classes são "Moldes":** A classe `CameraManager` não é a câmera, é a planta do projeto. Quando você faz `minha_camera = CameraManager()`, você cria um **Objeto** (uma instância real que liga o hardware).
2. **O poderoso `self`:** O `self` é como o objeto se refere a ele mesmo. Se o `CameraManager` tem uma variável `self.frame`, significa que "aquele frame pertence a esta câmera específica" e ficará guardado lá enquanto a câmera existir.
3. **Injeção de Dependência:** É um nome chique para: *"Não crie as coisas dentro da classe, receba elas prontas"*. 
   - ❌ Errado: O `ui.py` criar a câmera do zero lá dentro.
   - ✅ Certo: O `main.py` liga a câmera e passa ela para o `ui.py` como argumento. Assim a UI só "usa" o que já está pronto.

---

## 🚀 O Roteiro de Refatoração

Sua missão é migrar o `interface.py` atual para a pasta `app/`, fatiando-o em três partes.

### 🛡️ Missão 1: O Hardware (CameraManager)
**Arquivo Destino:** `app/backend.py`

* **Seu Desafio:** Vá no `interface.py` original, pegue a classe `CameraManager` inteira e mova para o `backend.py`. 
* **Regra de Ouro:** Essa classe é "surda e cega" para o resto do mundo. Ela não pode ter nenhum `import customtkinter`, não pode saber nada de YOLO, nem salvar arquivos.
* **O que ela faz:**
  - Inicia a Thread (`cv2.VideoCapture`).
  - Lê os frames e atualiza o `self._frame`.
  - Entrega o frame quando alguém pede (`get_frame()`).

> [!TIP]
> A sua classe atual no `interface.py` já está excelente! Preste atenção apenas para ver se ela não puxa nenhuma cor ou detalhe de tela sem querer.

---

### 🧠 Missão 2: O Especialista IA (VisionAnalyzer)
**Arquivo Destino:** `app/backend.py`

* **Seu Desafio:** Criar uma classe que cuide estritamente do modelo YOLO.
* **Como montar o `__init__`:** Ele deve receber o `model_path` (caminho do peso `.pt`) e carregar o `YOLO` na memória (`self.model = YOLO(...)`).
* **Como montar a ação:** Crie um método chamado `analisar_frame(self, frame)`. Esse método recebe uma imagem, passa no modelo, desenha as caixas (se quiser) e devolve o resultado para quem pediu.
* **Regra de Ouro:** O Especialista IA não liga a câmera. Ele apenas recebe uma foto e diz "tem anomalia ou não tem".

---

### 🎯 Missão 3: O Maestro (CaptureSession)
**Arquivo Destino:** `app/backend.py`

* **Seu Desafio:** É aqui que a mágica (e a lógica do antigo `batch_processor`) acontece.
* **Injeção de Dependência:** O `__init__(self, camera, analyzer)` recebe a câmera e a IA já prontas. Ele vai guardá-las (`self.camera = camera`, etc).
* **A Lógica de Negócio:** Crie um método `iniciar_exame(self)`. Esse método deve:
  1. Pegar um frame da câmera (`self.camera.get_frame()`).
  2. Salvar na pasta `capturas`.
  3. Mandar para a IA (`self.analyzer.analisar_frame()`).
  4. Salvar na pasta `analisadas`.
  5. Fazer isso 10 vezes controlando o tempo.

> [!IMPORTANT]
> Lembre-se que se essa lógica tiver um `while` demorado, ela pode "congelar" a interface depois. No futuro, você estudará como rodar o `iniciar_exame` dentro de uma *Thread* separada para a tela não travar!

---

### 🎨 Missão 4: A Pintura (ui.py)
**Arquivo Destino:** `app/ui.py`

* **Seu Desafio:** Pegar as classes visuais do `interface.py` (`ScreenT0`, `VisualDetectApp`, etc) e limpar toda a "sujeira" do backend delas.
* **Como limpar:** 
  - Remova qualquer menção a YOLO, `cv2.VideoCapture` e criação de pastas.
  - O `VisualDetectApp` (que agora você pode chamar de `VisualDetectUI`) deve receber o maestro no início: `__init__(self, sessao)`.
* **Como interagir:** Quando o usuário apertar o botão de iniciar ou a tecla "Enter", a UI não faz o trabalho. Ela apenas diz: `self.sessao.iniciar_exame()`.
* **Atualizando o vídeo:** A tela continuará chamando `sessao.camera.get_photo()` a cada 30ms para desenhar a imagem da webcam atualizada no label do CustomTkinter.

---

## 🏁 Testando o Sucesso

Se você fizer tudo certo, o seu `main.py` será lindo e limpo. Ele fará apenas isto:

```python
# 1. Cria a estrutura (backend)
camera = CameraManager()
ia = VisionAnalyzer("pesos.pt")
sessao = CaptureSession(camera, ia)

# 2. Cria a tela, passando a sessão para ela
tela = VisualDetectUI(sessao)

# 3. Liga tudo!
camera.start()
tela.mainloop()
```

Bom estudo! Tente ir copiando e colando os métodos do `interface.py` aos poucos. Tente executar o `main.py` constantemente a cada mudança para garantir que a tela continua abrindo, mesmo que as funções ainda não façam nada.
