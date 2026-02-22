"""
append_file — Adiciona conteúdo ao final de um arquivo existente.

Analogia Unix: echo >>
Input: path (str) — caminho relativo à raiz do gray_ocean
       content (str) — conteúdo a ser adicionado
Output: confirmação ou erro

Exemplo de uso:
    result = run(path="agents/architect/log.md", content="\\n## Ação 1\\n...")
"""

import os

TOOL_NAME = "append_file"
TOOL_DESCRIPTION = "Adiciona conteúdo ao final de um arquivo. Recebe 'path' (caminho relativo) e 'content' (conteúdo a adicionar)."
TOOL_PARAMETERS = {
    "path": "Caminho relativo ao arquivo",
    "content": "Conteúdo a ser adicionado ao final do arquivo"
}

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def run(path: str, content: str) -> str:
    """Adiciona conteúdo ao final de um arquivo."""
    full_path = os.path.join(BASE_DIR, path)
    full_path = os.path.normpath(full_path)

    # Segurança: não permitir traversal fora do gray_ocean
    if not full_path.startswith(BASE_DIR):
        return f"ERRO: Acesso negado. O caminho '{path}' está fora do gray_ocean."

    if not os.path.exists(full_path):
        return f"ERRO: Arquivo não encontrado: {path}. Use write_file para criar."

    try:
        with open(full_path, "a", encoding="utf-8") as f:
            f.write(content)

        return f"OK: Conteúdo adicionado a '{path}' ({len(content)} caracteres)."
    except Exception as e:
        return f"ERRO ao adicionar a '{path}': {e}"
