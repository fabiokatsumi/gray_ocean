"""
list_dir — Lista o conteúdo de um diretório no Gray Ocean.

Analogia Unix: ls
Input: path (str) — caminho relativo à raiz do gray_ocean (padrão: ".")
Output: lista de arquivos e diretórios formatada

Exemplo de uso:
    result = run(path="tools")
    result = run(path="agents")
"""

import os

TOOL_NAME = "list_dir"
TOOL_DESCRIPTION = "Lista o conteúdo de um diretório. Recebe 'path' (caminho relativo, padrão: raiz do gray_ocean)."
TOOL_PARAMETERS = {
    "path": "Caminho relativo ao diretório (padrão: '.')"
}

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def run(path: str = ".") -> str:
    """Lista arquivos e diretórios no caminho especificado."""
    full_path = os.path.join(BASE_DIR, path)
    full_path = os.path.normpath(full_path)

    # Segurança: não permitir traversal fora do gray_ocean
    if not full_path.startswith(BASE_DIR):
        return f"ERRO: Acesso negado. O caminho '{path}' está fora do gray_ocean."

    if not os.path.exists(full_path):
        return f"ERRO: Diretório não encontrado: {path}"

    if not os.path.isdir(full_path):
        return f"ERRO: '{path}' não é um diretório. Use read_file para arquivos."

    try:
        entries = sorted(os.listdir(full_path))
        if not entries:
            return f"Diretório '{path}' está vazio."

        lines = []
        for entry in entries:
            entry_path = os.path.join(full_path, entry)
            if os.path.isdir(entry_path):
                lines.append(f"  [DIR]  {entry}/")
            else:
                size = os.path.getsize(entry_path)
                lines.append(f"  [FILE] {entry} ({size} bytes)")

        header = f"Conteúdo de '{path}':\n"
        return header + "\n".join(lines)
    except Exception as e:
        return f"ERRO ao listar '{path}': {e}"
