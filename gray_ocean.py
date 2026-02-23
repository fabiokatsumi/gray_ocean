#!/usr/bin/env python3
"""
gray_ocean.py — Ponto de entrada do Gray Ocean Framework

O shell do Gray Ocean. Recebe mensagens em linguagem natural,
encaminha ao agente Architect (ou outro agente especificado),
e retorna a resposta.

Uso:
    python gray_ocean.py "sua mensagem aqui"
    python gray_ocean.py --agent nome_do_agente "sua mensagem"
    python gray_ocean.py --model llama3.1 "sua mensagem"
    python gray_ocean.py --interactive
"""


import sys
import os
import re
import argparse

# Adicionar o diretório raiz ao path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)
AGENTS_DIR = os.path.join(BASE_DIR, "agents")

from core.runtime import run_agent


def parse_at_mention(text: str) -> tuple:
    """
    Parses @agent_name from the beginning of a message.
    Returns (agent_name, remaining_message) if an existing agent is mentioned,
    or (None, original_text) otherwise.
    """
    match = re.match(r"^@([a-zA-Z_][a-zA-Z0-9_]*)\s*(.*)", text, re.DOTALL)
    if not match:
        return None, text
    agent_name = match.group(1).lower()
    message = match.group(2).strip()
    agent_dir = os.path.join(AGENTS_DIR, agent_name)
    if os.path.isdir(agent_dir):
        return agent_name, message if message else "hi"
    return None, text


def list_available_agents() -> list:
    """Returns a list of available agent names."""
    if not os.path.isdir(AGENTS_DIR):
        return []
    return sorted(
        d for d in os.listdir(AGENTS_DIR)
        if os.path.isdir(os.path.join(AGENTS_DIR, d)) and not d.startswith(".")
    )

# Load .env for model default
def load_env():
    env_path = os.path.join(BASE_DIR, ".env")
    env = {}
    if os.path.exists(env_path):
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    env[k.strip()] = v.strip()
    return env

ENV = load_env()
DEFAULT_MODEL = ENV.get("OLLAMA_MODEL") or ENV.get("OPENAI_MODEL") or ENV.get("OPENROUTER_MODEL") or "llama3.1:8b"


def print_banner():
    """Exibe o banner do Gray Ocean."""
    print(
        """
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
       GRAY OCEAN — Agent Framework
       "Começa como uma poça.
        Os agentes decidem o resto."
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    """
    )


def interactive_mode(agent: str, model: str):
    """Modo interativo — loop de conversa com o agente."""
    print_banner()
    agents = list_available_agents()
    print(f"  Agente padrão: {agent} | Modelo: {model}")
    print(f"  Agentes disponíveis: {', '.join('@' + a for a in agents)}")
    print("  Use @nome_agente mensagem para falar com um agente específico.")
    print("  Digite 'sair' ou 'exit' para encerrar.\n")

    while True:
        try:
            user_input = input("  > ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\n\n  Até logo.")
            break

        if not user_input:
            continue

        if user_input.lower() in ("sair", "exit", "quit"):
            print("\n  Até logo.")
            break

        target_agent = agent
        message = user_input

        mentioned_agent, remaining = parse_at_mention(user_input)
        if mentioned_agent:
            target_agent = mentioned_agent
            message = remaining

        print()
        try:
            run_agent(target_agent, message, model=model)
            print()  # blank line after streamed response
        except FileNotFoundError as e:
            print(f"  ERRO: {e}\n")
        except Exception as e:
            print(f"  ERRO inesperado: {e}\n")


def single_message(agent: str, message: str, model: str):
    """Modo single-shot — envia uma mensagem e retorna."""
    mentioned_agent, remaining = parse_at_mention(message)
    if mentioned_agent:
        agent = mentioned_agent
        message = remaining

    try:
        run_agent(agent, message, model=model)
        # Response is streamed to stdout by call_llm(); no re-print needed
    except FileNotFoundError as e:
        print(f"ERRO: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"ERRO inesperado: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="Gray Ocean — Framework de Agentes Auto-Evolutivos",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos:
  python gray_ocean.py "liste todas as tools disponíveis"
  python gray_ocean.py "crie uma tool que calcula fibonacci"
  python gray_ocean.py --agent architect "preciso de um agente monitor"
  python gray_ocean.py --interactive
  python gray_ocean.py --model llama3.1:8b "olá"
        """,
    )

    parser.add_argument(
        "message",
        nargs="?",
        help="Mensagem em linguagem natural para o agente",
    )
    parser.add_argument(
        "--agent", "-a",
        default="architect",
        help="Nome do agente a ser invocado (padrão: architect)",
    )
    parser.add_argument(
        "--model", "-m",
        default=DEFAULT_MODEL,
        help="Modelo LLM a usar (default: definido em .env)",
    )
    parser.add_argument(
        "--interactive", "-i",
        action="store_true",
        help="Modo interativo (loop de conversa)",
    )

    args = parser.parse_args()

    if args.interactive:
        interactive_mode(args.agent, args.model)
    elif args.message:
        single_message(args.agent, args.message, args.model)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
