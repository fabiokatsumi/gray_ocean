"""
ask_llm — Faz uma chamada ao LLM via Ollama local.

Analogia Unix: curl para API
Input: prompt (str) — a mensagem para o LLM
       system (str, opcional) — system prompt
       model (str, opcional) — modelo a usar (padrão: llama3.1)
Output: resposta do LLM como string

Exemplo de uso:
    result = run(prompt="Escreva uma função fibonacci em Python")
"""

import json
import urllib.request
import urllib.error

TOOL_NAME = "ask_llm"
TOOL_DESCRIPTION = "Faz uma pergunta ao LLM (Ollama local). Recebe 'prompt' (mensagem), opcionalmente 'system' (system prompt) e 'model' (modelo)."
TOOL_PARAMETERS = {
    "prompt": "A mensagem/pergunta para o LLM",
    "system": "(Opcional) System prompt para contextualizar o LLM",
    "model": "(Opcional) Modelo a usar. Padrão: llama3.1"
}

OLLAMA_URL = "http://localhost:11434/api/generate"
DEFAULT_MODEL = "llama3.1"


def run(prompt: str, system: str = "", model: str = "") -> str:
    """Envia prompt ao Ollama e retorna a resposta."""
    if not model:
        model = DEFAULT_MODEL

    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
    }

    if system:
        payload["system"] = system

    try:
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            OLLAMA_URL,
            data=data,
            headers={"Content-Type": "application/json"},
        )

        with urllib.request.urlopen(req, timeout=120) as response:
            result = json.loads(response.read().decode("utf-8"))
            return result.get("response", "ERRO: Resposta vazia do LLM.")

    except urllib.error.URLError as e:
        return (
            f"ERRO: Não foi possível conectar ao Ollama em {OLLAMA_URL}. "
            f"Verifique se o Ollama está rodando (ollama serve). Detalhe: {e}"
        )
    except json.JSONDecodeError as e:
        return f"ERRO: Resposta inválida do Ollama: {e}"
    except Exception as e:
        return f"ERRO ao chamar LLM: {e}"
