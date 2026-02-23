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
import argparse

# Adicionar o diretório raiz ao path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

from core.runtime import run_agent

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
    print(f"  Agente: {agent} | Modelo: {model}")
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

        print()
        try:
            response = run_agent(agent, user_input, model=model)
            print(f"  {response}\n")
        except FileNotFoundError as e:
            print(f"  ERRO: {e}\n")
        except Exception as e:
            print(f"  ERRO inesperado: {e}\n")


def single_message(agent: str, message: str, model: str):
    """Modo single-shot — envia uma mensagem e retorna."""
    try:
        response = run_agent(agent, message, model=model)
        print(response)
    except FileNotFoundError as e:
        print(f"ERRO: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"ERRO inesperado: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        # Debug: print Ollama connection info if relevant
        if hasattr(e, 'reason') or 'ollama' in str(e).lower():
            print("[DEBUG] Verifique se o Ollama está rodando e acessível em http://localhost:11434")
            print("[DEBUG] Detalhes do erro:", repr(e))
            print("[DEBUG] Variáveis de ambiente relevantes:")
            print("  OLLAMA_HOST:", os.environ.get('OLLAMA_HOST'))
            print("  OLLAMA_BASE_URL:", os.environ.get('OLLAMA_BASE_URL'))
        sys.exit(1)


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
