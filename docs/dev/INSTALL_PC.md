# VisualDetect — Instalação e Execução no PC (Windows)

> Guia para desenvolvedores rodarem o VisualDetect no computador durante o desenvolvimento.

---

## Pré-requisitos

- Python 3.10 ou superior instalado
- Git instalado
- Webcam USB conectada (opcional — a câmera fica desabilitada se não estiver disponível)

---

## 1. Clonar o repositório

```powershell
git clone https://github.com/MYuri-beck/visual-detect.git
cd visual-detect
```

---

## 2. Criar e ativar o ambiente virtual

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

> Após ativar, o terminal mostra `(.venv)` no início da linha.

---

## 3. Instalar dependências

```powershell
pip install -r requirements_pc.txt
```

> **Nota:** O `requirements_pc.txt` inclui todas as dependências necessárias para rodar
> no PC (YOLO, OpenCV, PyTorch, customtkinter, etc.).

---

## 4. Colocar o modelo treinado

O modelo `.pt` não é versionado no GitHub. Copie-o para dentro da pasta `app/`:

```
app/
└── models/
    └── best.pt   ← coloque aqui com EXATAMENTE este nome
```

> Se o modelo não estiver presente, o app inicia normalmente mas sem detecção YOLO.

---

## 5. Rodar a aplicação

```powershell
# Abrir o terminal na raiz do projeto (VisualDetect/) e rodar:
.venv\Scripts\python.exe app\main.py
```

A janela abre em **800×480** px — resolução do display do Raspberry Pi.

---

## 6. Navegação durante o desenvolvimento

| Tecla       | Ação                        |
|-------------|-----------------------------|
| `←` / `→`  | Selecionar botão / voltar   |
| `↑` / `↓`  | Ajustar valor (tela T2)     |
| `Enter`     | Confirmar / avançar tela    |
| `F11`       | Alternar fullscreen         |
| `Esc`       | Sair do fullscreen / fechar |

---

## 7. Onde ficam as fotos capturadas

Ambas as pastas são criadas automaticamente dentro de `app/` ao rodar o primeiro exame:

| Pasta | Conteúdo |
|-------|----------|
| `app/capturas_voluntarios_analisar/` | Fotos brutas da câmera |
| `app/capturas_analisadas_voluntarios/` | Fotos com anotações YOLO |

---

## 8. Parâmetros configuráveis

Edite `app/main.py` para ajustar:

| Constante        | Padrão              | O que muda                          |
|------------------|---------------------|-------------------------------------|
| `MODELO_PATH`    | `app/models/best.pt`| Caminho para o modelo YOLO          |
| `CAPTURE_FOLDER` | `app/capturas_*/`   | Pasta de fotos brutas               |
| `ANALYZED_FOLDER`| `app/capturas_*/`   | Pasta de fotos analisadas           |

Edite `app/backend.py` para ajustar padrões do exame:

| Atributo        | Padrão | O que muda                         |
|-----------------|--------|------------------------------------|
| `image_number`  | `10`   | Número de fotos por exame          |
| `total_time`    | `10`   | Duração total do exame (segundos)  |

---

## Dúvidas?

Consulte o README raiz ou abra uma issue no GitHub:  
https://github.com/MYuri-beck/visual-detect/issues
