"""
write_file — Cria ou sobrescreve um arquivo no Gray Ocean.

Analogia Unix: echo >
Input: path (str) — caminho relativo à raiz do gray_ocean
       content (str) — conteúdo a ser escrito
Output: confirmação ou erro

Exemplo de uso:
    result = run(path="tools/nova_tool.py", content="def run(): ...")
"""

import os

TOOL_NAME = "write_file"
TOOL_DESCRIPTION = "Cria ou sobrescreve um arquivo. Recebe 'path' (caminho relativo) e 'content' (conteúdo)."
TOOL_PARAMETERS = {
    "path": "Caminho relativo ao arquivo a ser criado/sobrescrito",
    "content": "Conteúdo a ser escrito no arquivo"
}

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def run(path: str, content: str) -> str:
    """Cria ou sobrescreve um arquivo com o conteúdo fornecido."""
    full_path = os.path.join(BASE_DIR, path)
    full_path = os.path.normpath(full_path)

    # Segurança: não permitir traversal fora do gray_ocean
    if not full_path.startswith(BASE_DIR):
        return f"ERRO: Acesso negado. O caminho '{path}' está fora do gray_ocean."

    try:
        # Cria diretórios intermediários se necessário
        dir_path = os.path.dirname(full_path)
        if dir_path and not os.path.exists(dir_path):
            os.makedirs(dir_path, exist_ok=True)

        with open(full_path, "w", encoding="utf-8") as f:
            f.write(content)

        return f"OK: Arquivo '{path}' escrito com sucesso ({len(content)} caracteres)."
    except Exception as e:
        return f"ERRO ao escrever '{path}': {e}"
