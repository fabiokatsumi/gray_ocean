"""
spawn_agent — Cria um novo agente no Gray Ocean.

Analogia Unix: fork + mkdir
Input: name (str) — nome do agente
       purpose (str) — propósito/missão do agente
       tools (list[str]) — lista de nomes de tools autorizadas
       personality (str, opcional) — traços de personalidade
Output: confirmação ou erro

Exemplo de uso:
    result = run(
        name="monitor",
        purpose="Monitora mudanças em arquivos do gray ocean",
        tools=["read_file", "list_dir", "append_file"],
        personality="Vigilante, metódico, reporta anomalias com clareza"
    )
"""

import os
from datetime import datetime

TOOL_NAME = "spawn_agent"
TOOL_DESCRIPTION = "Cria um novo agente com sua pasta e 5 arquivos .md. Recebe 'name', 'purpose', 'tools' (lista de tools autorizadas), e opcionalmente 'personality'."
TOOL_PARAMETERS = {
    "name": "Nome do agente (usado como nome da pasta)",
    "purpose": "Propósito/missão do agente",
    "tools": "Lista de nomes de tools que o agente pode usar",
    "personality": "(Opcional) Traços de personalidade do agente"
}

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AGENTS_DIR = os.path.join(BASE_DIR, "agents")


def run(name: str, purpose: str, tools: list = None, personality: str = "") -> str:
    """Cria a pasta do agente com seus 5 arquivos .md."""
    if tools is None:
        tools = []

    # Validação
    safe_name = name.lower().replace(" ", "_").replace("-", "_")
    if not safe_name.isidentifier():
        return f"ERRO: Nome '{name}' inválido para agente."

    agent_dir = os.path.join(AGENTS_DIR, safe_name)
    if os.path.exists(agent_dir):
        return f"ERRO: Agente '{safe_name}' já existe em agents/{safe_name}/."

    today = datetime.now().strftime("%Y-%m-%d")
    tools_list = ", ".join(tools) if tools else "nenhuma"
    tools_md_items = "\n".join(f"- `{t}`" for t in tools) if tools else "- (nenhuma tool atribuída)"

    if not personality:
        personality = "Focado, eficiente, comunica resultados com clareza."

    # Conteúdo dos 5 arquivos .md
    files = {
        "README.md": f"""# Agente: {safe_name}

## Propósito
{purpose}

## Criado em
{today}

## Tools Autorizadas
{tools_list}

## Inputs
- Mensagens em linguagem natural relacionadas à sua missão

## Outputs
- Respostas em texto com resultados das ações executadas
- Registros no log.md de cada ação
""",
        "personality.md": f"""# Personalidade — {safe_name}

{personality}

## Estilo de Comunicação
- Responde de forma objetiva e clara
- Registra suas ações e raciocínio
- Quando não sabe algo, diz explicitamente
- Erros são reportados com contexto para diagnóstico
""",
        "system_prompt.md": f"""# System Prompt — {safe_name}

Você é o agente **{safe_name}** do Gray Ocean framework.

## Sua Missão
{purpose}

## Regras
1. Use APENAS as tools listadas em tools.md
2. Registre TODA ação no log.md usando append_file
3. Quando não souber como resolver algo, diga explicitamente
4. Siga os valores do VALUES.md em todas as decisões
5. Prefira soluções simples sobre soluções complexas

## Formato de Resposta
Quando precisar usar uma tool, responda EXATAMENTE neste formato:

TOOL: nome_da_tool
ARGS:
param1: valor1
param2: valor2

Quando terminar a tarefa, responda com:

DONE: sua resposta final aqui
""",
        "tools.md": f"""# Tools Autorizadas — {safe_name}

Este agente tem acesso às seguintes tools:

{tools_md_items}

> Princípio de menor privilégio: este agente acessa APENAS estas tools.
> Para solicitar acesso a tools adicionais, a mudança deve ser aprovada.
""",
        "log.md": f"""# Log — {safe_name}

## {today} — Criação
- Agente criado pelo sistema
- Propósito: {purpose}
- Tools autorizadas: {tools_list}

---
""",
    }

    try:
        os.makedirs(agent_dir, exist_ok=True)

        for filename, content in files.items():
            filepath = os.path.join(agent_dir, filename)
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(content)

        return (
            f"OK: Agente '{safe_name}' criado com sucesso em agents/{safe_name}/.\n"
            f"Arquivos criados: {', '.join(files.keys())}\n"
            f"Tools autorizadas: {tools_list}"
        )

    except Exception as e:
        return f"ERRO ao criar agente '{safe_name}': {e}"
