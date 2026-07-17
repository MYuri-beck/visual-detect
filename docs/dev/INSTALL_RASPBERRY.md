# VisualDetect — Guia de Instalação no Raspberry Pi

> Guia para desenvolvedores e técnicos configurarem o hardware dedicado.
> Para o guia do usuário final (médico), consulte [`docs/user_guide/GUIA_DO_USUARIO.md`](../user_guide/GUIA_DO_USUARIO.md).

---

## Índice

1. [O que você vai precisar](#1-o-que-você-vai-precisar)
2. [Tutorial: Criar e usar a branch raspberry-pi](#2-tutorial-criar-e-usar-a-branch-raspberry-pi)
3. [Tutorial: Instalar o Raspberry Pi OS](#3-tutorial-instalar-o-raspberry-pi-os)
4. [Tutorial: Configuração inicial do Raspberry Pi](#4-tutorial-configuração-inicial-do-raspberry-pi)
5. [Tutorial: Instalar o VisualDetect](#5-tutorial-instalar-o-visualdetect)
6. [Onde colocar o modelo `.pt`](#6-onde-colocar-o-modelo-pt)
7. [Parâmetros configuráveis](#7-parâmetros-configuráveis)
8. [Tutorial: Configurar autostart (hardware dedicado)](#8-tutorial-configurar-autostart-hardware-dedicado)
9. [Comandos do dia a dia](#9-comandos-do-dia-a-dia)
10. [Solução de problemas](#10-solução-de-problemas)

---

## 1. O que você vai precisar

| Item | Descrição |
|---|---|
| Raspberry Pi 4 | 4GB ou 8GB de RAM recomendado |
| Cartão microSD | Mínimo 32GB, classe 10 ou A1 |
| Fonte de alimentação | USB-C, 5V/3A (oficial da Raspberry Pi) |
| Monitor ou tela TFT | Conexão HDMI (ou SPI para telas TFT) |
| Webcam USB | Testada com câmeras UVC padrão |
| Cabo HDMI | MicroHDMI → HDMI (o Pi 4 usa microHDMI) |
| Teclado + Mouse USB | Só para a configuração inicial |
| Computador com Windows/Mac | Para gravar o cartão SD |

---

## 2. Tutorial: Criar e usar a branch raspberry-pi

> **O que é uma branch?** É uma "linha do tempo paralela" do seu código no Git.
> A branch `main` tem o código de desenvolvimento geral.
> A branch `raspberry-pi` tem tudo configurado para o hardware dedicado.
> Você pode alternar entre elas sem perder nada.

### Por que criar uma branch separada?

- Mantém o código de desenvolvimento limpo
- Pode ter configurações específicas do Raspberry Pi sem afetar o código principal
- Facilita atualizar o hardware quando houver mudanças

### Como criar a branch (passo a passo)

#### No terminal do seu computador (Windows/PowerShell ou terminal do Raspberry Pi):

```bash
# 1. Certifique-se de estar na branch principal
git checkout main

# 2. Crie a nova branch e já mude para ela
git checkout -b raspberry-pi

# O -b significa "criar e mudar para esta branch ao mesmo tempo"
# Sem o -b, o git checkout só troca de branch sem criar
```

#### Verificar em qual branch você está:

```bash
git branch

# A saída será algo assim:
#   main
# * raspberry-pi       ← o asterisco indica a branch atual
```

#### Enviar a branch para o GitHub:

```bash
# Na primeira vez, precisa dizer ao git onde enviar (-u = upstream)
git push -u origin raspberry-pi

# Nas próximas vezes, basta:
git push
```

#### Trocar entre branches:

```bash
git checkout main          # volta para a principal
git checkout raspberry-pi  # vai para a do Raspberry Pi
```

#### Atualizar a branch raspberry-pi com mudanças do main:

```bash
# Estando na branch raspberry-pi:
git merge main
# Isso traz todas as mudanças do main para cá
```

---

## 3. Tutorial: Instalar o Raspberry Pi OS

### Passo 1 — Baixar o Raspberry Pi Imager

1. No seu computador, acesse: **https://www.raspberrypi.com/software/**
2. Clique em **"Download for Windows"** (ou Mac)
3. Instale o programa normalmente

### Passo 2 — Gravar o cartão SD

1. Insira o cartão microSD no computador (use um adaptador se necessário)
2. Abra o **Raspberry Pi Imager**
3. Clique em **"Choose Device"** → selecione **Raspberry Pi 4**
4. Clique em **"Choose OS"** → selecione:
   - **Raspberry Pi OS (64-bit)** ← recomendado para IA/YOLO
   - ⚠️ Escolha a versão **com Desktop** (não Lite, pois precisamos da interface gráfica)
5. Clique em **"Choose Storage"** → selecione seu cartão SD
6. Clique na engrenagem ⚙️ **antes de gravar** para configurar:

### Passo 3 — Configurações avançadas (clique na engrenagem ⚙️)

```
✅ Set hostname: visualdetect.local
✅ Enable SSH: sim (para acessar remotamente depois)
✅ Set username and password:
      Username: pi
      Password: (escolha uma senha segura)
✅ Configure wireless LAN: (coloque o Wi-Fi se for usar)
✅ Set locale settings:
      Timezone: America/Sao_Paulo
      Keyboard layout: pt (Portuguese)
```

> **Por que configurar aqui?** Assim o Pi já sobe configurado, sem precisar de teclado/mouse para a configuração inicial.

7. Clique em **"Save"** e depois **"Write"**
8. Aguarde a gravação e verificação (pode demorar 5–15 minutos)

### Passo 4 — Primeira inicialização

1. Remova o cartão do computador e insira no Raspberry Pi
2. Conecte o monitor (cabo microHDMI → HDMI)
3. Conecte teclado e mouse USB
4. Conecte a webcam USB
5. Por último, conecte a fonte de alimentação (isso liga o Pi)
6. Aguarde a inicialização (primeira vez pode demorar 2–3 minutos)

---

## 4. Tutorial: Configuração inicial do Raspberry Pi

### Acessar o terminal

No desktop do Raspberry Pi, abra o **Terminal** (ícone na barra de tarefas) ou pressione `Ctrl + Alt + T`.

### Verificar se a câmera USB é detectada

```bash
ls /dev/video*
# Deve aparecer: /dev/video0  /dev/video1  etc.

# Ver detalhes da câmera:
v4l2-ctl --list-devices
```

### Atualizar o sistema (sempre faça isso primeiro)

```bash
sudo apt-get update && sudo apt-get upgrade -y
```

> Isso pode demorar 10–20 minutos na primeira vez.

### Habilitar a câmera (apenas câmeras CSI — não necessário para USB)

```bash
sudo raspi-config
# Interface Options → Camera → Enable
# Sair e reiniciar
```

---

## 5. Tutorial: Instalar o VisualDetect

### Passo 1 — Clonar o repositório

```bash
# Navegue até onde quer instalar o projeto (ex: pasta home do usuário pi)
cd /home/pi

# Clone o repositório
git clone https://github.com/MYuri-beck/visual-detect.git VisualDetect

# Explicação do parâmetro:
# VisualDetect     → nome da pasta que será criada
```

### Passo 2 — Entrar na pasta

```bash
cd VisualDetect
```

### Passo 3 — Rodar o script de instalação automática

```bash
bash docs/dev/install_rpi.sh
```

> O script cuida de tudo: dependências, ambiente virtual e autostart.
> Pode demorar 20–40 minutos, dependendo da sua conexão e do Pi.

### Instalação manual (caso prefira fazer passo a passo)

Se quiser entender o que acontece por baixo:

```bash
# 1. Instalar dependências do sistema
sudo apt-get install -y python3-pip python3-venv python3-tk python3-dev \
    libgl1-mesa-glx libglib2.0-0 libsm6 libxext6 libxrender-dev \
    libatlas-base-dev libjpeg-dev libopenblas-dev v4l-utils git

# 2. Criar ambiente virtual
python3 -m venv .venv

# 3. Ativar o ambiente virtual
source .venv/bin/activate
# (Você verá (.venv) aparecer no início do terminal)

# 4. Atualizar o pip
pip install --upgrade pip

# 5. Instalar dependências Python
pip install -r requirements_pc.txt
pip install -r requirements_rpi.txt

# 6. Testar se funciona
python app/main.py --fullscreen
```

---

## 6. Onde colocar o modelo `.pt`

O modelo treinado (arquivo `.pt`) é o "cérebro" do sistema — ele não é versionado no GitHub por ser um arquivo grande.

### Localização

```
VisualDetect/
└── app/
    └── models/
        └── best.pt   ← coloque seu modelo aqui com EXATAMENTE este nome
```

> **Nota:** O modelo fica dentro de `app/models/` pois a pasta `app/` é autocontida —
> é ela que vai para o Raspberry Pi.

### Como transferir o modelo para o Raspberry Pi

**Opção A — Pendrive USB:**
```bash
# No Raspberry Pi, com o pendrive inserido:
cp /media/pi/<nome-do-pendrive>/best.pt /home/pi/VisualDetect/app/models/best.pt
```

**Opção B — SCP (transferir pelo Wi-Fi):**
```bash
# No seu computador Windows (PowerShell):
scp C:\caminho\para\best.pt pi@visualdetect.local:/home/pi/VisualDetect/app/models/best.pt

# Explicação:
# scp = "secure copy" — copia arquivos pela rede com segurança
# pi@visualdetect.local = usuário pi no endereço visualdetect.local
```

**Opção C — Google Drive / WeTransfer:**
```bash
# No Raspberry Pi com o link de download direto:
wget -O /home/pi/VisualDetect/app/models/best.pt "URL_DO_DOWNLOAD"
```

### Verificar se o modelo está no lugar certo

```bash
ls -lh /home/pi/VisualDetect/app/models/
# Deve aparecer: best.pt  (com tamanho em MB)
```

---

## 7. Parâmetros configuráveis

Todos os parâmetros ficam no arquivo **`app/main.py`**. Edite com:

```bash
nano /home/pi/VisualDetect/app/main.py
```

> **Como usar o nano:** edite o texto normalmente. Para salvar: `Ctrl+O` → Enter. Para sair: `Ctrl+X`.

### Tabela completa de parâmetros

| Parâmetro | Onde fica | Valor padrão | O que muda se você alterar |
|---|---|---|---|
| `MODELO_PATH` | `app/main.py` linha ~31 | `models/best.pt` | Qual arquivo de modelo YOLO é carregado. Mude se seu modelo tiver outro nome. |
| `CAPTURE_FOLDER` | `app/main.py` linha ~39 | `capturas_voluntarios_analisar` | Pasta onde as fotos brutas do exame são salvas. |
| `ANALYZED_FOLDER` | `app/main.py` linha ~43 | `capturas_analisadas_voluntarios` | Pasta onde as fotos com as marcações do YOLO são salvas. |
| `image_number` | `app/backend.py` linha ~225 | `10` | Quantas fotos são tiradas por exame. Mais fotos = mais dados, mas exame mais lento. |
| `total_time` | `app/backend.py` linha ~226 | `10` | Duração total do exame em segundos. Ex: 10 fotos em 10s = 1 foto/segundo. |
| `index` da câmera | `app/backend.py` → `CameraManager.start(index)` | `0` | Qual câmera usar. `0` = primeira câmera detectada. Se tiver duas câmeras, tente `1`. |
| `--fullscreen` | linha de comando | desativado | Abre a janela em tela cheia. Essencial para hardware dedicado. |

### Exemplos de ajuste

**Exame mais rápido (5 fotos em 5 segundos):**
```python
# Em app/backend.py:
self.image_number = 5
self.total_time = 5
```

**Exame mais detalhado (20 fotos em 30 segundos):**
```python
self.image_number = 20
self.total_time = 30
```

**Mudar pasta de capturas:**
```python
# Em app/main.py:
CAPTURE_FOLDER = "exames/fotos_brutas"
ANALYZED_FOLDER = "exames/fotos_analisadas"
```

**Usar uma câmera diferente (segunda câmera USB):**
```python
# Em app/main.py:
camera = CameraManager()
camera.start(1)  # índice 1 = segunda câmera
```

---

## 8. Tutorial: Configurar autostart (hardware dedicado)

O autostart faz o VisualDetect abrir **automaticamente ao ligar o Raspberry Pi**, sem precisar de teclado, mouse ou login manual — como um equipamento médico dedicado.

### O que é o systemd?

O `systemd` é o gerenciador de serviços do Linux. É ele quem controla o que inicia junto com o sistema (como o Wi-Fi, o Bluetooth, etc.). Vamos registrar o VisualDetect como mais um serviço.

### Instalação automática (via script)

Se você usou o `install_rpi.sh`, o autostart já está configurado! Basta reiniciar:

```bash
sudo reboot
```

### Instalação manual (passo a passo explicado)

#### Passo 1 — Editar o arquivo de serviço

```bash
nano /home/pi/VisualDetect/docs/dev/visualdetect.service
```

Localize as linhas com `/home/pi/VisualDetect` e confirme que o caminho está correto para onde você clonou o projeto.

#### Passo 2 — Copiar o arquivo para o systemd

```bash
sudo cp /home/pi/VisualDetect/docs/dev/visualdetect.service /etc/systemd/system/

# Explicação:
# sudo = executa como administrador (root)
# cp = copia arquivo
# /etc/systemd/system/ = pasta onde o systemd procura serviços
```

#### Passo 3 — Recarregar o systemd

```bash
sudo systemctl daemon-reload
# Diz ao systemd para ler os novos arquivos de serviço
```

#### Passo 4 — Habilitar o serviço (iniciar no boot)

```bash
sudo systemctl enable visualdetect.service
# "enable" = registra para iniciar automaticamente no boot
# Diferente de "start" que apenas inicia agora
```

#### Passo 5 — Iniciar agora para testar (sem reiniciar)

```bash
sudo systemctl start visualdetect.service
```

#### Passo 6 — Verificar se está funcionando

```bash
sudo systemctl status visualdetect.service

# Saída esperada (algo assim):
# ● visualdetect.service - VisualDetect — Detecção de Retinoblastoma
#      Loaded: loaded (/etc/systemd/system/visualdetect.service; enabled)
#      Active: active (running)   ← deve aparecer "active (running)"
```

#### Passo 7 — Reiniciar para testar o autostart

```bash
sudo reboot
# Após reiniciar, o app deve abrir sozinho em tela cheia
```

### Como desabilitar o autostart temporariamente

```bash
sudo systemctl disable visualdetect.service
# O app ainda pode ser iniciado manualmente, mas não inicia no boot
```

### Como parar o app remotamente (via SSH)

```bash
sudo systemctl stop visualdetect.service
```

---

## 9. Comandos do dia a dia

### Verificar logs do app

```bash
# Ver os logs mais recentes
journalctl -u visualdetect --since today

# Acompanhar em tempo real (Ctrl+C para sair)
journalctl -u visualdetect -f

# Ver os últimos 50 erros
journalctl -u visualdetect -n 50
```

### Atualizar o código (quando tiver mudanças no GitHub)

```bash
cd /home/pi/VisualDetect
git pull                                # baixa as mudanças
sudo systemctl restart visualdetect    # reinicia o app com o novo código
```

### Verificar câmera

```bash
ls /dev/video*          # lista câmeras disponíveis
v4l2-ctl --list-devices # mostra nome e fabricante de cada câmera
```

### Verificar uso de memória/CPU

```bash
htop
# Interface visual (Ctrl+C para sair)
```

### Acessar remotamente via SSH (do seu computador)

```bash
# No Windows PowerShell:
ssh pi@visualdetect.local

# Se não funcionar o nome, use o IP (descubra com: hostname -I no Pi)
ssh pi@192.168.1.XXX
```

---

## 10. Solução de problemas

### O app não abre / tela preta

```bash
# Ver o erro exato
journalctl -u visualdetect -n 30

# Verificar se o modelo existe
ls -lh /home/pi/VisualDetect/app/models/best.pt

# Testar manualmente (desliga o serviço primeiro)
sudo systemctl stop visualdetect
cd /home/pi/VisualDetect
source .venv/bin/activate
python app/main.py --fullscreen
```

### Câmera não detectada

```bash
# Verificar se o sistema vê a câmera
ls /dev/video*

# Testar a câmera
python3 -c "import cv2; cap=cv2.VideoCapture(0); print('Câmera OK' if cap.isOpened() else 'ERRO'); cap.release()"

# Se tiver duas câmeras, tente o índice 1:
# Edite app/main.py → camera.start(1)
```

### Erro "model not found"

```bash
# Confirme o caminho do modelo
ls -lh /home/pi/VisualDetect/app/models/

# O arquivo deve se chamar exatamente: best.pt
# Se o nome for diferente, renomeie:
mv /home/pi/VisualDetect/app/models/seu_modelo.pt /home/pi/VisualDetect/app/models/best.pt
```

### App fica lento / travando

```bash
# Verificar temperatura (Pi throttla quando esquenta)
vcgencmd measure_temp

# Verificar uso de memória
free -h

# Verificar se está usando swap (sinal de pouca RAM)
swapon --show
```

### O app inicia mas não aparece na tela

O systemd pode iniciar antes da interface gráfica estar pronta.

```bash
# Editar o serviço
sudo nano /etc/systemd/system/visualdetect.service

# Adicionar um delay após [Service]:
ExecStartPre=/bin/sleep 5

# Salvar e reiniciar
sudo systemctl daemon-reload
sudo systemctl restart visualdetect
```

---

## Estrutura do projeto

```
VisualDetect/
├── app/                                  ← pasta autocontida (deploy no Raspberry Pi)
│   ├── main.py                           ← ponto de entrada; configure parâmetros aqui
│   ├── backend.py                        ← lógica de câmera, YOLO e sessão de captura
│   ├── ui.py                             ← interface gráfica
│   ├── assets/                           ← logos da interface
│   ├── models/
│   │   └── best.pt                       ← coloque seu modelo aqui (não versionado)
│   ├── capturas_voluntarios_analisar/    ← criada automaticamente ao rodar
│   └── capturas_analisadas_voluntarios/  ← criada automaticamente ao rodar
│
├── docs/
│   ├── dev/
│   │   ├── INSTALL_RASPBERRY.md   ← este arquivo
│   │   ├── INSTALL_PC.md          ← guia para Windows
│   │   ├── install_rpi.sh         ← script de instalação automática
│   │   └── visualdetect.service   ← serviço systemd para autostart
│   └── user_guide/
│       └── GUIA_DO_USUARIO.md     ← guia para o médico
│
├── requirements_pc.txt     ← dependências Python para PC e Raspberry Pi
└── requirements_rpi.txt    ← dependências extras do Raspberry Pi
```

---

*Dúvidas? Abra uma issue no GitHub: https://github.com/MYuri-beck/visual-detect/issues*
