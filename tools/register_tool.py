"""
register_tool — Registra uma nova tool no Gray Ocean.

Analogia Unix: install
Input: name (str) — nome da tool (sem .py)
       code (str) — código Python da tool (deve ter função run())
       description (str) — descrição curta da tool
Output: confirmação ou erro

Exemplo de uso:
    result = run(
        name="fibonacci",
        code="def run(n: int) -> str:\\n    ...",
        description="Calcula o n-ésimo número de Fibonacci"
    )
"""

import os
from datetime import datetime

TOOL_NAME = "register_tool"
TOOL_DESCRIPTION = "Registra uma nova tool no gray ocean. Recebe 'name' (nome), 'code' (código Python com run()) e 'description' (descrição)."
TOOL_PARAMETERS = {
    "name": "Nome da tool (sem extensão .py)",
    "code": "Código Python da tool (deve conter função run())",
    "description": "Descrição curta do que a tool faz"
}

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOOLS_DIR = os.path.join(BASE_DIR, "tools")
INDEX_PATH = os.path.join(TOOLS_DIR, "index.md")


def run(name: str, code: str, description: str) -> str:
    """Salva uma nova tool como .py e atualiza o index.md."""
    # Validação do nome
    if not name.isidentifier():
        return f"ERRO: Nome '{name}' inválido. Use apenas letras, números e underscores."

    # Verificar se já existe
    tool_path = os.path.join(TOOLS_DIR, f"{name}.py")
    if os.path.exists(tool_path):
        return f"ERRO: Tool '{name}' já existe. Edite o arquivo diretamente se quiser modificar."

    # Verificar se o código contém função run()
    if "def run(" not in code:
        return "ERRO: O código deve conter uma função run(). Padrão: def run(...) -> str:"

    try:
        # Salvar o arquivo da tool
        with open(tool_path, "w", encoding="utf-8") as f:
            f.write(code)

        # Atualizar o index.md
        today = datetime.now().strftime("%Y-%m-%d")
        entry = f"\n### `{name}`\n- **Arquivo:** `tools/{name}.py`\n- **Descrição:** {description}\n- **Registrada em:** {today}\n- **Origem:** criada por agente\n"

        with open(INDEX_PATH, "a", encoding="utf-8") as f:
            f.write(entry)

        return f"OK: Tool '{name}' registrada com sucesso em tools/{name}.py e adicionada ao index.md."

    except Exception as e:
        # Limpar em caso de erro parcial
        if os.path.exists(tool_path):
            os.unlink(tool_path)
        return f"ERRO ao registrar tool '{name}': {e}"
