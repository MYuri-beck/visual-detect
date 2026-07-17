#!/bin/bash
# =============================================================================
# install_rpi.sh — VisualDetect: Instalação automática no Raspberry Pi
# =============================================================================
# Execute este script UMA VEZ após clonar o repositório:
#
#   bash docs/dev/install_rpi.sh
#
# O script vai:
#   1. Atualizar o sistema
#   2. Instalar dependências do sistema via apt
#   3. Criar o ambiente virtual Python
#   4. Instalar as bibliotecas Python
#   5. Registrar o serviço de autostart (systemd)
# =============================================================================

set -e  # Para imediatamente se qualquer comando falhar

# --- Cores para o terminal ---
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # Sem cor

# --- Diretório raiz do projeto ---
# O script está em docs/dev/, então sobe dois níveis (docs/dev → docs → raiz)
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
echo -e "${BLUE}=================================================${NC}"
echo -e "${BLUE}   VisualDetect — Instalação Raspberry Pi${NC}"
echo -e "${BLUE}=================================================${NC}"
echo -e "Diretório do projeto: ${GREEN}${PROJECT_DIR}${NC}"
echo ""

# =============================================================================
# PASSO 1 — Atualizar o sistema
# =============================================================================
echo -e "${YELLOW}[1/5] Atualizando lista de pacotes...${NC}"
sudo apt-get update -y

# =============================================================================
# PASSO 2 — Instalar dependências do sistema
# =============================================================================
echo -e "${YELLOW}[2/5] Instalando dependências do sistema...${NC}"
sudo apt-get install -y \
    python3-pip \
    python3-venv \
    python3-tk \
    python3-dev \
    libgl1 \
    libgl1-mesa-dri \
    libglib2.0-0t64 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libjpeg-dev \
    libopenblas-dev \
    v4l-utils \
    git

echo -e "${GREEN}  ✓ Dependências do sistema instaladas.${NC}"

# =============================================================================
# PASSO 3 — Criar ambiente virtual Python
# =============================================================================
echo -e "${YELLOW}[3/5] Criando ambiente virtual Python...${NC}"
cd "$PROJECT_DIR"

if [ -d ".venv" ]; then
    echo "  Ambiente virtual já existe. Pulando criação."
else
    python3 -m venv .venv
    echo -e "${GREEN}  ✓ Ambiente virtual criado em .venv/${NC}"
fi

# Ativa o ambiente virtual
source .venv/bin/activate

# =============================================================================
# PASSO 4 — Instalar bibliotecas Python
# =============================================================================
echo -e "${YELLOW}[4/5] Instalando bibliotecas Python...${NC}"

# Atualiza o pip primeiro
pip install --upgrade pip

# Instala dependências principais
echo "  Instalando requirements_pc.txt..."
pip install -r requirements_pc.txt

# Instala dependências específicas do Raspberry Pi
echo "  Instalando requirements_rpi.txt..."
pip install -r requirements_rpi.txt

echo -e "${GREEN}  ✓ Bibliotecas Python instaladas.${NC}"

# =============================================================================
# PASSO 5 — Registrar serviço de autostart
# =============================================================================
echo -e "${YELLOW}[5/5] Configurando autostart (systemd)...${NC}"

# Substitui o caminho do projeto no arquivo de serviço
SERVICE_TEMPLATE="$PROJECT_DIR/docs/dev/visualdetect.service"
SERVICE_DEST="/etc/systemd/system/visualdetect.service"
SERVICE_TEMP="/tmp/visualdetect.service"

# Substitui o placeholder pelo caminho real do projeto
sed "s|/home/pi/VisualDetect|$PROJECT_DIR|g" "$SERVICE_TEMPLATE" > "$SERVICE_TEMP"

# Copia o serviço para o systemd
sudo cp "$SERVICE_TEMP" "$SERVICE_DEST"

# Recarrega e habilita o serviço
sudo systemctl daemon-reload
sudo systemctl enable visualdetect.service

echo -e "${GREEN}  ✓ Serviço visualdetect registrado e habilitado.${NC}"

# =============================================================================
# CONCLUSÃO
# =============================================================================
echo ""
echo -e "${BLUE}=================================================${NC}"
echo -e "${GREEN}  INSTALAÇÃO CONCLUÍDA COM SUCESSO!${NC}"
echo -e "${BLUE}=================================================${NC}"
echo ""
echo -e "Próximos passos:"
echo -e "  1. Coloque seu modelo em: ${YELLOW}${PROJECT_DIR}/app/models/best.pt${NC}"
echo -e "  2. Reinicie o Raspberry Pi: ${YELLOW}sudo reboot${NC}"
echo -e "  3. O app iniciará automaticamente."
echo ""
echo -e "Comandos úteis:"
echo -e "  Ver logs:    ${YELLOW}journalctl -u visualdetect -f${NC}"
echo -e "  Parar app:   ${YELLOW}sudo systemctl stop visualdetect${NC}"
echo -e "  Iniciar app: ${YELLOW}sudo systemctl start visualdetect${NC}"
echo -e "  Status:      ${YELLOW}sudo systemctl status visualdetect${NC}"
echo ""
