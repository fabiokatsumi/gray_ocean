#!/bin/bash
# setup.sh — Configuração do Gray Ocean
#
# Instala o Ollama e baixa o modelo padrão (llama3.1).
# Uso: bash setup.sh

set -e

echo ""
echo "  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
echo "     GRAY OCEAN — Setup"
echo "  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
echo ""

# 1. Verificar Python
echo "[1/3] Verificando Python..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version 2>&1)
    echo "  OK: $PYTHON_VERSION"
else
    echo "  ERRO: Python 3 não encontrado. Instale Python 3.8+ e tente novamente."
    exit 1
fi

# 2. Instalar Ollama
echo ""
echo "[2/3] Verificando Ollama..."
if command -v ollama &> /dev/null; then
    echo "  OK: Ollama já está instalado."
else
    echo "  Ollama não encontrado. Instalando..."
    curl -fsSL https://ollama.com/install.sh | sh
    echo "  OK: Ollama instalado."
fi

# 3. Baixar modelo
echo ""
echo "[3/3] Verificando modelo llama3.1..."
if ollama list 2>/dev/null | grep -q "llama3.1"; then
    echo "  OK: Modelo llama3.1 já disponível."
else
    echo "  Baixando modelo llama3.1 (pode demorar)..."
    ollama pull llama3.1
    echo "  OK: Modelo llama3.1 baixado."
fi

echo ""
echo "  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
echo "     Setup completo!"
echo ""
echo "     Para usar:"
echo "     python3 gray_ocean.py \"sua mensagem\""
echo ""
echo "     Para modo interativo:"
echo "     python3 gray_ocean.py --interactive"
echo "  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
echo ""
