"""
ask_llm — Makes a call to the LLM via the provider configured in .env.

Unix analog: curl for API
Input: prompt (str) — the message for the LLM
       system (str, optional) — system prompt
       model (str, optional) — model to use (default: defined in .env)
Output: LLM response as string
"""

import json
import os
import urllib.request
import urllib.error

TOOL_NAME = "ask_llm"
TOOL_DESCRIPTION = "Asks a question to the LLM using the provider configured in .env (ollama/openai/openrouter). Receives 'prompt' (message), optionally 'system' (system prompt) and 'model' (model)."
TOOL_PARAMETERS = {
    "prompt": "The message/question for the LLM",
    "system": "(Optional) System prompt to contextualize the LLM",
    "model": "(Optional) Model to use. Default: defined in .env",
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
                return result.get("message", {}).get("content", "ERROR: Empty response from LLM.")

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
                return f"ERROR: {provider} API {resp.status_code}: {resp.text}"
            return resp.json()["choices"][0]["message"]["content"]

        else:
            return f"ERROR: LLM_PROVIDER '{provider}' not supported. Use: ollama, openai, openrouter."

    except urllib.error.URLError as e:
        return f"ERROR: Could not connect to LLM ({provider}). Details: {e}"
    except Exception as e:
        return f"ERROR calling LLM: {e}"
