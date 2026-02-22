"""
runtime.py — O Kernel do Gray Ocean

Implementa o loop ReAct (Reason + Act) para execução de agentes.

Fluxo:
1. Carrega o agente a partir de seus arquivos .md
2. Constrói o system prompt injetando personalidade + tools disponíveis
3. Envia mensagem do humano para o LLM
4. Parseia a resposta: é TOOL ou DONE?
5. Se TOOL: executa a tool, injeta resultado, volta ao passo 3
6. Se DONE: registra no log, retorna resposta ao humano
7. Se max_steps atingido: retorna o que tiver e loga o timeout
"""

import os
import sys
import json
import importlib.util
from datetime import datetime

# Raiz do gray_ocean
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOOLS_DIR = os.path.join(BASE_DIR, "tools")
AGENTS_DIR = os.path.join(BASE_DIR, "agents")

MAX_STEPS = 15


def load_agent(agent_name: str) -> dict:
    """Carrega um agente a partir de seus arquivos .md."""
    agent_dir = os.path.join(AGENTS_DIR, agent_name)

    if not os.path.isdir(agent_dir):
        raise FileNotFoundError(f"Agente '{agent_name}' não encontrado em {agent_dir}")

    agent = {"name": agent_name, "dir": agent_dir}

    md_files = {
        "readme": "README.md",
        "personality": "personality.md",
        "system_prompt": "system_prompt.md",
        "tools": "tools.md",
        "log": "log.md",
    }

    for key, filename in md_files.items():
        filepath = os.path.join(agent_dir, filename)
        if os.path.exists(filepath):
            with open(filepath, "r", encoding="utf-8") as f:
                agent[key] = f.read()
        else:
            agent[key] = ""

    return agent


def parse_authorized_tools(tools_md: str) -> list:
    """Extrai a lista de tools autorizadas do tools.md do agente."""
    tools = []
    for line in tools_md.split("\n"):
        line = line.strip()
        if line.startswith("- `") and line.endswith("`"):
            tool_name = line[3:-1]
            tools.append(tool_name)
    return tools


def load_tool(tool_name: str):
    """Carrega dinamicamente um módulo de tool."""
    tool_path = os.path.join(TOOLS_DIR, f"{tool_name}.py")

    if not os.path.exists(tool_path):
        return None

    spec = importlib.util.spec_from_file_location(tool_name, tool_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def build_tools_description(tool_names: list) -> str:
    """Constrói a descrição de tools disponíveis para o system prompt."""
    descriptions = []

    for name in tool_names:
        module = load_tool(name)
        if module:
            desc = getattr(module, "TOOL_DESCRIPTION", "Sem descrição")
            params = getattr(module, "TOOL_PARAMETERS", {})
            params_str = "\n".join(f"    {k}: {v}" for k, v in params.items())
            descriptions.append(
                f"### {name}\n{desc}\nParâmetros:\n{params_str}"
            )

    return "\n\n".join(descriptions)


def build_system_prompt(agent: dict, tool_names: list) -> str:
    """Monta o system prompt completo para o agente."""
    tools_desc = build_tools_description(tool_names)

    # Carregar VALUES.md se existir
    values_path = os.path.join(BASE_DIR, "VALUES.md")
    values = ""
    if os.path.exists(values_path):
        with open(values_path, "r", encoding="utf-8") as f:
            values = f.read()

    prompt = f"""{agent.get('system_prompt', '')}

---
## Personalidade
{agent.get('personality', '')}

---
## Tools Disponíveis
{tools_desc}

---
## Formato de Uso de Tools

Quando precisar usar uma tool, responda EXATAMENTE neste formato (uma tool por vez):

TOOL: nome_da_tool
ARGS:
param1: valor1
param2: valor2

Para argumentos com múltiplas linhas, use o delimitador <<<>>> :

TOOL: nome_da_tool
ARGS:
param1: valor simples
param2: <<<
conteúdo com
múltiplas linhas
aqui
>>>

Quando terminar completamente a tarefa, responda com:

DONE: sua resposta final aqui

---
## Valores do Sistema
{values}
"""
    return prompt


def parse_llm_response(response: str) -> dict:
    """Parseia a resposta do LLM para identificar TOOL ou DONE."""
    response = response.strip()

    # Verificar DONE
    if "DONE:" in response:
        idx = response.index("DONE:")
        return {
            "type": "DONE",
            "content": response[idx + 5:].strip(),
            "reasoning": response[:idx].strip() if idx > 0 else "",
        }

    # Verificar TOOL
    if "TOOL:" in response:
        idx = response.index("TOOL:")
        reasoning = response[:idx].strip() if idx > 0 else ""
        rest = response[idx:]

        lines = rest.split("\n")
        tool_name = lines[0].replace("TOOL:", "").strip()

        args = {}
        if len(lines) > 1:
            i = 1
            # Pular linha "ARGS:" se existir
            if i < len(lines) and lines[i].strip().upper().startswith("ARGS"):
                i += 1

            current_key = None
            multiline_value = None
            in_multiline = False

            while i < len(lines):
                line = lines[i]

                if in_multiline:
                    if line.strip() == ">>>":
                        args[current_key] = multiline_value
                        in_multiline = False
                        current_key = None
                        multiline_value = None
                    else:
                        if multiline_value:
                            multiline_value += "\n" + line
                        else:
                            multiline_value = line
                elif ":" in line and not line.startswith(" " * 4):
                    # Nova chave:valor
                    colon_idx = line.index(":")
                    key = line[:colon_idx].strip()
                    value = line[colon_idx + 1:].strip()

                    if key and key not in ("TOOL", "ARGS"):
                        current_key = key
                        if value == "<<<":
                            in_multiline = True
                            multiline_value = ""
                        else:
                            args[key] = value

                i += 1

        return {
            "type": "TOOL",
            "tool": tool_name,
            "args": args,
            "reasoning": reasoning,
        }

    # Se não tem TOOL nem DONE, tratar como DONE implícito
    return {
        "type": "DONE",
        "content": response,
        "reasoning": "",
    }


def execute_tool(tool_name: str, args: dict, authorized_tools: list) -> str:
    """Executa uma tool com os argumentos fornecidos."""
    if tool_name not in authorized_tools:
        return f"ERRO: Tool '{tool_name}' não autorizada para este agente. Tools autorizadas: {', '.join(authorized_tools)}"

    module = load_tool(tool_name)
    if module is None:
        return f"ERRO: Tool '{tool_name}' não encontrada em tools/."

    if not hasattr(module, "run"):
        return f"ERRO: Tool '{tool_name}' não possui função run()."

    try:
        # Converter tipos de argumentos conforme necessário
        import inspect
        sig = inspect.signature(module.run)
        converted_args = {}

        for param_name, param in sig.parameters.items():
            if param_name in args:
                value = args[param_name]
                annotation = param.annotation

                if annotation == list or (
                    hasattr(annotation, "__origin__")
                    and annotation.__origin__ == list
                ):
                    # Tentar parsear como JSON list
                    if isinstance(value, str):
                        try:
                            value = json.loads(value)
                        except json.JSONDecodeError:
                            # Tentar parsear como lista separada por vírgula
                            value = [v.strip() for v in value.split(",")]
                    converted_args[param_name] = value
                elif annotation == int:
                    converted_args[param_name] = int(value)
                elif annotation == float:
                    converted_args[param_name] = float(value)
                elif annotation == bool:
                    converted_args[param_name] = value.lower() in (
                        "true", "1", "yes", "sim"
                    )
                else:
                    converted_args[param_name] = value
            elif param.default is not inspect.Parameter.empty:
                pass  # Usa o default da função
            else:
                return (
                    f"ERRO: Parâmetro obrigatório '{param_name}' não fornecido "
                    f"para tool '{tool_name}'."
                )

        result = module.run(**converted_args)
        return str(result)

    except Exception as e:
        return f"ERRO ao executar tool '{tool_name}': {e}"


def log_action(agent: dict, action: str):
    """Registra uma ação no log.md do agente."""
    log_path = os.path.join(agent["dir"], "log.md")
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    entry = f"\n## {timestamp}\n{action}\n"

    try:
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(entry)
    except Exception:
        pass  # Log não deve interromper a execução


def call_llm(system_prompt: str, messages: list, model: str = "llama3.1") -> str:
    """Chama o LLM via Ollama com histórico de mensagens."""
    import urllib.request
    import urllib.error

    url = "http://localhost:11434/api/chat"

    payload = {
        "model": model,
        "messages": [{"role": "system", "content": system_prompt}] + messages,
        "stream": False,
    }

    try:
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            url,
            data=data,
            headers={"Content-Type": "application/json"},
        )

        with urllib.request.urlopen(req, timeout=120) as response:
            result = json.loads(response.read().decode("utf-8"))
            message = result.get("message", {})
            return message.get("content", "ERRO: Resposta vazia do LLM.")

    except urllib.error.URLError as e:
        return (
            f"ERRO: Não foi possível conectar ao Ollama. "
            f"Verifique se o Ollama está rodando (ollama serve). Detalhe: {e}"
        )
    except Exception as e:
        return f"ERRO ao chamar LLM: {e}"


def run_agent(agent_name: str, user_message: str, model: str = "llama3.1") -> str:
    """
    Executa o loop ReAct completo para um agente.

    1. Carrega o agente
    2. Constrói o system prompt
    3. Envia mensagem → LLM
    4. Parseia resposta (TOOL ou DONE)
    5. Se TOOL: executa, injeta resultado, repete
    6. Se DONE: loga e retorna
    7. Se max_steps: retorna com aviso
    """
    # 1. Carregar agente
    agent = load_agent(agent_name)

    # 2. Identificar tools autorizadas
    authorized_tools = parse_authorized_tools(agent.get("tools", ""))

    # 3. Construir system prompt
    system_prompt = build_system_prompt(agent, authorized_tools)

    # 4. Iniciar conversa
    messages = [{"role": "user", "content": user_message}]

    log_action(agent, f"- Recebeu mensagem: {user_message[:200]}...")

    # 5. Loop ReAct
    for step in range(1, MAX_STEPS + 1):
        # Chamar LLM
        llm_response = call_llm(system_prompt, messages, model)

        if llm_response.startswith("ERRO:"):
            log_action(agent, f"- ERRO no LLM (step {step}): {llm_response}")
            return llm_response

        # Parsear resposta
        parsed = parse_llm_response(llm_response)

        if parsed["type"] == "DONE":
            # Tarefa concluída
            final_response = parsed["content"]
            log_action(
                agent,
                f"- Tarefa concluída (step {step})\n- Resposta: {final_response[:300]}..."
            )
            return final_response

        elif parsed["type"] == "TOOL":
            tool_name = parsed["tool"]
            tool_args = parsed["args"]
            reasoning = parsed.get("reasoning", "")

            log_action(
                agent,
                f"- Step {step}: Tool={tool_name}, Args={json.dumps(tool_args, ensure_ascii=False)[:200]}"
            )

            # Executar tool
            tool_result = execute_tool(tool_name, tool_args, authorized_tools)

            log_action(
                agent,
                f"- Resultado tool '{tool_name}': {tool_result[:200]}..."
            )

            # Adicionar à conversa
            messages.append({"role": "assistant", "content": llm_response})
            messages.append({
                "role": "user",
                "content": f"Resultado da tool '{tool_name}':\n{tool_result}"
            })

    # Max steps atingido
    timeout_msg = (
        f"AVISO: Limite de {MAX_STEPS} passos atingido. "
        f"Último estado da conversa retornado."
    )
    log_action(agent, f"- TIMEOUT: {MAX_STEPS} passos atingidos")
    return timeout_msg
