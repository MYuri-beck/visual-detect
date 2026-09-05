# VisualDetect — Instalação e Execução no PC (Windows)

> **Público:** Desenvolvedores que querem rodar o VisualDetect no Windows durante o desenvolvimento.
> Para o deploy no hardware dedicado, consulte [INSTALL_RASPBERRY.md](INSTALL_RASPBERRY.md).

---

## Índice

1. [Pré-requisitos](#1-pré-requisitos)
2. [Clonar o repositório](#2-clonar-o-repositório)
3. [Criar e ativar o ambiente virtual](#3-criar-e-ativar-o-ambiente-virtual)
4. [Instalar dependências](#4-instalar-dependências)
5. [Colocar o modelo treinado](#5-colocar-o-modelo-treinado)
6. [Rodar a aplicação](#6-rodar-a-aplicação)
7. [Navegação pelo teclado](#7-navegação-pelo-teclado)
8. [Onde ficam as fotos capturadas](#8-onde-ficam-as-fotos-capturadas)
9. [Parâmetros configuráveis](#9-parâmetros-configuráveis)
10. [Solução de problemas](#10-solução-de-problemas)
11. [Fluxo de desenvolvimento](#11-fluxo-de-desenvolvimento)

---

## 1. Pré-requisitos

Antes de começar, certifique-se de ter instalado:

| Requisito | Versão mínima | Como verificar |
|---|---|---|
| Python | 3.10+ | `python --version` |
| Git | qualquer | `git --version` |
| pip | incluído no Python | `pip --version` |

> **Webcam USB:** Opcional — a câmera fica desabilitada graciosamente se não estiver disponível.
> A interface funciona normalmente para testes de navegação sem câmera.

---

## 2. Clonar o repositório

Abra o **PowerShell** e rode:

```powershell
git clone https://github.com/MYuri-beck/visual-detect.git
cd visual-detect
```

---

## 3. Criar e ativar o ambiente virtual

```powershell
# Criar o ambiente virtual na pasta .venv
python -m venv .venv

# Ativar
.venv\Scripts\Activate.ps1
```

Após ativar, o terminal mostra `(.venv)` no início da linha:

```
(.venv) PS C:\...\visual-detect>
```

> **Erro de permissão no Activate.ps1?** Execute uma vez como administrador:
> ```powershell
> Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
> ```

---

## 4. Instalar dependências

```powershell
pip install -r requirements_pc.txt
```

O processo instala automaticamente:
- `ultralytics` (YOLO)
- `opencv-python` (câmera)
- `torch` + `torchvision` (PyTorch — pode demorar, ~1–2 GB)
- `customtkinter` (interface gráfica)
- `Pillow`, `numpy`, `matplotlib`, `scikit-learn`

> **Demorou muito?** O PyTorch é grande (~1-2 GB). Normal demorar 5–15 minutos dependendo
> da conexão. Aguarde a conclusão antes de prosseguir.

---

## 5. Colocar o modelo treinado

O modelo `.pt` não é versionado no GitHub. Coloque-o em:

```
visual-detect/
└── app/
    └── models/
        └── best.pt   ← nome EXATO obrigatório
```

```powershell
# Crie a pasta se não existir:
New-Item -ItemType Directory -Force -Path "app\models"

# Copie seu modelo (ajuste o caminho):
Copy-Item "C:\caminho\para\seu_modelo.pt" "app\models\best.pt"
```

> Se o modelo não estiver presente, o app inicia normalmente mas sem detecção YOLO —
> útil para testar a interface sem rodar a IA.

---

## 6. Rodar a aplicação

Com o ambiente virtual ativado e na raiz do projeto:

```powershell
# Janela 800×480 (resolução do display do Raspberry Pi)
.venv\Scripts\python.exe app\main.py

# Ou com Python ativo no PATH:
python app\main.py
```

A janela abre em **800×480 px** — mesma resolução do hardware final, para fidelidade visual.

---

## 7. Navegação pelo teclado

No PC, use o teclado para simular os botões físicos do Pico 2W:

| Tecla | Ação | Telas onde funciona |
|---|---|---|
| `←` (seta esquerda) | Voltar / selecionar botão esquerdo | T2, T3, T5, Galeria |
| `→` (seta direita) | Avançar / selecionar botão direito | T1, T3, T5 |
| `↑` (seta cima) | Aumentar valor / item acima | T1, T2, Galeria |
| `↓` (seta baixo) | Diminuir valor / item abaixo | T1, T2, Galeria |
| `Enter` | Confirmar / avançar tela | Todas |
| `F11` | Alternar fullscreen | Todas |
| `Esc` | Sair do fullscreen / fechar | Todas |

---

## 8. Onde ficam as fotos capturadas

As pastas são criadas automaticamente ao rodar o primeiro exame:

| Pasta | Conteúdo |
|---|---|
| `app/capturas_voluntarios_analisar/` | Fotos brutas da câmera |
| `app/capturas_analisadas_voluntarios/` | Fotos com anotações YOLO (bounding boxes) |

Formato dos nomes: `AAAAMMDD_HHMMSS_capture_N.jpg`

---

## 9. Parâmetros configuráveis

### Em `app/main.py`

| Constante | Padrão | O que muda |
|---|---|---|
| `MODELO_PATH` | `app/models/best.pt` | Caminho para o modelo YOLO |
| `CAPTURE_FOLDER` | `app/capturas_voluntarios_analisar` | Pasta de fotos brutas |
| `ANALYZED_FOLDER` | `app/capturas_analisadas_voluntarios` | Pasta de fotos analisadas |

### Em `app/backend.py`

| Atributo | Padrão | O que muda |
|---|---|---|
| `image_number` | `10` | Número de fotos por exame |
| `total_time` | `10` | Duração total do exame (segundos) |

---

## 10. Solução de problemas

### `pip install` falha em `torch`

```powershell
# Tente instalar o torch separadamente primeiro:
pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu

# Depois instale o resto:
pip install -r requirements_pc.txt
```

### `ModuleNotFoundError: No module named 'cv2'`

```powershell
pip install opencv-python
```

### `ModuleNotFoundError: No module named 'customtkinter'`

```powershell
pip install customtkinter
```

### A janela não abre / erro de display

No Windows, verifique se o ambiente virtual está ativado:

```powershell
# O terminal deve mostrar (.venv) no início
# Se não mostrar, ative:
.venv\Scripts\Activate.ps1
```

### Câmera não aparece na tela de Revisão

```python
# Em app/backend.py, tente índice 1 (segunda câmera):
camera.start(1)
```

### O app abre mas a detecção YOLO não funciona

1. Confirme que `app/models/best.pt` existe
2. Verifique o log no terminal — ele imprime o caminho do modelo ao iniciar
3. O modelo deve ser compatível com `ultralytics` 8.4+

### `UnicodeDecodeError` ao iniciar

```powershell
# Force UTF-8 no terminal:
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
```

---

## 11. Fluxo de desenvolvimento

### Ciclo básico

```
1. Editar código (app/ui.py, app/backend.py, app/main.py)
2. Salvar
3. Rodar: python app\main.py
4. Testar na janela 800×480
5. Repetir
```

### Testar sem câmera

O sistema detecta automaticamente a ausência de câmera e exibe uma mensagem na tela de revisão.
Todos os fluxos de navegação funcionam normalmente.

### Testar sem modelo YOLO

Remova ou renomeie `app/models/best.pt`. O app sobe, mas as telas T4/T4b completam sem detecção.
Útil para testar a UX de navegação isoladamente.

### Simular o Pico 2W

No PC, as setas do teclado + Enter simulam exatamente o comportamento dos botões físicos.
Não é necessário ter o Pico conectado durante o desenvolvimento.

---

*Dúvidas? Abra uma issue: https://github.com/MYuri-beck/visual-detect/issues*
