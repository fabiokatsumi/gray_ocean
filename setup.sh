#!/bin/bash
# setup.sh — Configuração do Gray Ocean
#
# Instala o Ollama e baixa o modelo padrão (llama3.1).
# Uso: bash setup.sh

set -e

echo ""
echo "  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
echo "     Setup completo!"
echo ""
echo "     Para usar:"

# 1. Verificar Python e criar ambiente isolado com uv
echo "[1/4] Verificando Python..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version 2>&1)
    echo "  OK: $PYTHON_VERSION"
else
    echo "  ERRO: Python 3 não encontrado. Instale Python 3.8+ e tente novamente."
    exit 1
fi

# 2. Instalar uv se necessário
echo ""
echo "[2/4] Verificando uv (ambiente isolado)..."
if command -v uv &> /dev/null; then
    echo "  OK: uv já está instalado."
else
    echo "  uv não encontrado. Instalando via pipx..."
    if command -v pipx &> /dev/null; then
        pipx install uv
    else
        python3 -m pip install --user uv
    fi
    echo "  OK: uv instalado."
fi

# 3. Criar ambiente isolado com uv
echo ""
echo "[3/4] Criando ambiente isolado com uv..."
if [ ! -d ".venv" ]; then
    uv venv .venv
    echo "  OK: Ambiente .venv criado."
else
    echo "  OK: Ambiente .venv já existe."
fi

# Ativar ambiente
echo "  Ativando ambiente .venv..."
source .venv/bin/activate
echo "  Ambiente ativado."

# 4. Instalar Ollama
echo ""
echo "[4/4] Verificando Ollama..."
if command -v ollama &> /dev/null; then
    echo "  OK: Ollama já está instalado."
else
    echo "  Ollama não encontrado. Instalando..."
    curl -fsSL https://ollama.com/install.sh | sh
    echo "  OK: Ollama instalado."
fi

# 5. Baixar modelo
echo ""
echo "[Extra] Verificando modelo llama3.1..."
if ollama list 2>/dev/null | grep -q "llama3.1"; then
    echo "  OK: Modelo llama3.1 já disponível."
else
    echo "  Baixando modelo llama3.1 (pode demorar)..."
    ollama pull llama3.1
    echo "  OK: Modelo llama3.1 baixado."
fi

echo "     python3 gray_ocean.py \"sua mensagem\""
echo ""
echo "     Para modo interativo:"
echo "     python3 gray_ocean.py --interactive"
echo "  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
echo ""
