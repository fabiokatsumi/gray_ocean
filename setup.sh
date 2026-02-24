#!/bin/bash
# setup.sh — Gray Ocean Setup
#
# Installs Ollama and downloads the default model (llama3.1).
# Usage: bash setup.sh

set -e

echo ""
echo "  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
echo "     Setup complete!"
echo ""
echo "     To use:"

# 1. Check Python and create isolated environment with uv
echo "[1/4] Checking Python..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version 2>&1)
    echo "  OK: $PYTHON_VERSION"
else
    echo "  ERROR: Python 3 not found. Install Python 3.8+ and try again."
    exit 1
fi

# 2. Install uv if needed
echo ""
echo "[2/4] Checking uv (isolated environment)..."
if command -v uv &> /dev/null; then
    echo "  OK: uv is already installed."
else
    echo "  uv not found. Installing via pipx..."
    if command -v pipx &> /dev/null; then
        pipx install uv
    else
        python3 -m pip install --user uv
    fi
    echo "  OK: uv installed."
fi

# 3. Create isolated environment with uv
echo ""
echo "[3/4] Creating isolated environment with uv..."
if [ ! -d ".venv" ]; then
    uv venv .venv
    echo "  OK: .venv environment created."
else
    echo "  OK: .venv environment already exists."
fi

# Activate environment
echo "  Activating .venv environment..."
source .venv/bin/activate
echo "  Environment activated."

# 4. Install Ollama
echo ""
echo "[4/4] Checking Ollama..."
if command -v ollama &> /dev/null; then
    echo "  OK: Ollama is already installed."
else
    echo "  Ollama not found. Installing..."
    curl -fsSL https://ollama.com/install.sh | sh
    echo "  OK: Ollama installed."
fi

# 5. Download model
echo ""
echo "[Extra] Checking llama3.1 model..."
if ollama list 2>/dev/null | grep -q "llama3.1"; then
    echo "  OK: llama3.1 model already available."
else
    echo "  Downloading llama3.1 model (may take a while)..."
    ollama pull llama3.1
    echo "  OK: llama3.1 model downloaded."
fi

echo "     python3 gray_ocean.py \"your message\""
echo ""
echo "     For interactive mode:"
echo "     python3 gray_ocean.py --interactive"
echo "  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
echo ""
