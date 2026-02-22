"""
read_file — Lê o conteúdo de um arquivo do Gray Ocean.

Analogia Unix: cat
Input: path (str) — caminho relativo à raiz do gray_ocean
Output: conteúdo do arquivo como string

Exemplo de uso:
    result = run(path="tools/index.md")
"""

import os

TOOL_NAME = "read_file"
TOOL_DESCRIPTION = "Lê o conteúdo de um arquivo. Recebe 'path' (caminho relativo à raiz do gray_ocean)."
TOOL_PARAMETERS = {
    "path": "Caminho relativo ao arquivo a ser lido"
}

# Raiz do gray_ocean (diretório pai de tools/)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def run(path: str) -> str:
    """Lê e retorna o conteúdo de um arquivo."""
    full_path = os.path.join(BASE_DIR, path)
    full_path = os.path.normpath(full_path)

    # Segurança: não permitir traversal fora do gray_ocean
    if not full_path.startswith(BASE_DIR):
        return f"ERRO: Acesso negado. O caminho '{path}' está fora do gray_ocean."

    if not os.path.exists(full_path):
        return f"ERRO: Arquivo não encontrado: {path}"

    if not os.path.isfile(full_path):
        return f"ERRO: '{path}' não é um arquivo. Use list_dir para diretórios."

    try:
        with open(full_path, "r", encoding="utf-8") as f:
            content = f.read()
        return content
    except Exception as e:
        return f"ERRO ao ler '{path}': {e}"
