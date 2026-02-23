"""
ask_llm — Faz uma chamada ao LLM via provider configurado em .env.

Analogia Unix: curl para API
Input: prompt (str) — a mensagem para o LLM
       system (str, opcional) — system prompt
       model (str, opcional) — modelo a usar (padrão: definido em .env)
Output: resposta do LLM como string
"""

import json
import os
import urllib.request
import urllib.error

TOOL_NAME = "ask_llm"
TOOL_DESCRIPTION = "Faz uma pergunta ao LLM usando o provider configurado em .env (ollama/openai/openrouter). Recebe 'prompt' (mensagem), opcionalmente 'system' (system prompt) e 'model' (modelo)."
TOOL_PARAMETERS = {
    "prompt": "A mensagem/pergunta para o LLM",
    "system": "(Opcional) System prompt para contextualizar o LLM",
    "model": "(Opcional) Modelo a usar. Padrão: definido em .env",
}


def _load_env() -> dict:
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    env_path = os.path.join(base_dir, ".env")
    env = {}
    if os.path.exists(env_path):
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    env[k.strip()] = v.strip()
    return env


def run(prompt: str, system: str = "", model: str = "") -> str:
    """Sends prompt to the configured LLM provider and returns the response."""
    import requests

    env = _load_env()
    provider = env.get("LLM_PROVIDER", "ollama").lower()

    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})

    try:
        if provider == "ollama":
            if not model:
                model = env.get("OLLAMA_MODEL", "llama3.1:8b")
            ollama_host = env.get("OLLAMA_HOST", "http://localhost:11434")
            url = f"{ollama_host}/api/chat"
            payload = {"model": model, "messages": messages, "stream": False}
            data = json.dumps(payload).encode("utf-8")
            req = urllib.request.Request(
                url, data=data, headers={"Content-Type": "application/json"}
            )
            with urllib.request.urlopen(req, timeout=120) as response:
                result = json.loads(response.read().decode("utf-8"))
                return result.get("message", {}).get("content", "ERRO: Resposta vazia do LLM.")

        elif provider in ("openai", "openrouter"):
            if provider == "openai":
                if not model:
                    model = env.get("OPENAI_MODEL", "gpt-4")
                api_key = env.get("OPENAI_API_KEY", "")
                url = "https://api.openai.com/v1/chat/completions"
            else:
                if not model:
                    model = env.get("OPENROUTER_MODEL", "meta-llama-3")
                api_key = env.get("OPENROUTER_API_KEY", "")
                url = "https://openrouter.ai/api/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            }
            payload = {"model": model, "messages": messages, "temperature": 0.7, "stream": False}
            resp = requests.post(url, headers=headers, json=payload, timeout=120)
            if resp.status_code != 200:
                return f"ERRO: {provider} API {resp.status_code}: {resp.text}"
            return resp.json()["choices"][0]["message"]["content"]

        else:
            return f"ERRO: LLM_PROVIDER '{provider}' não suportado. Use: ollama, openai, openrouter."

    except urllib.error.URLError as e:
        return f"ERRO: Não foi possível conectar ao LLM ({provider}). Detalhe: {e}"
    except Exception as e:
        return f"ERRO ao chamar LLM: {e}"
