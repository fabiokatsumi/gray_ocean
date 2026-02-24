#!/usr/bin/env python3
"""
gray_ocean.py — Entry point of the Gray Ocean Framework

The Gray Ocean shell. Receives natural language messages,
forwards them to the Architect agent (or another specified agent),
and returns the response.

Usage:
    python gray_ocean.py "your message here"
    python gray_ocean.py --agent agent_name "your message"
    python gray_ocean.py --model llama3.1 "your message"
    python gray_ocean.py --interactive
"""


import sys
import os
import re
import argparse

# Add the root directory to the path
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
    """Displays the Gray Ocean banner."""
    print(
        """
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
       GRAY OCEAN — Agent Framework
       "Starts as a puddle.
        Agents decide the rest."
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    """
    )


def interactive_mode(agent: str, model: str):
    """Interactive mode — conversation loop with the agent."""
    print_banner()
    agents = list_available_agents()
    print(f"  Default agent: {agent} | Model: {model}")
    print(f"  Available agents: {', '.join('@' + a for a in agents)}")
    print("  Use @agent_name message to talk to a specific agent.")
    print("  Type 'exit' or 'quit' to end the session.\n")

    while True:
        try:
            user_input = input("  > ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\n\n  Goodbye.")
            break

        if not user_input:
            continue

        if user_input.lower() in ("exit", "quit"):
            print("\n  Goodbye.")
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
            print(f"  ERROR: {e}\n")
        except Exception as e:
            print(f"  Unexpected ERROR: {e}\n")


def single_message(agent: str, message: str, model: str):
    """Single-shot mode — sends a message and returns."""
    mentioned_agent, remaining = parse_at_mention(message)
    if mentioned_agent:
        agent = mentioned_agent
        message = remaining

    try:
        run_agent(agent, message, model=model)
        # Response is streamed to stdout by call_llm(); no re-print needed
    except FileNotFoundError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected ERROR: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="Gray Ocean — Self-Evolving Agent Framework",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python gray_ocean.py "list all available tools"
  python gray_ocean.py "create a tool that calculates fibonacci"
  python gray_ocean.py --agent architect "I need a monitor agent"
  python gray_ocean.py --interactive
  python gray_ocean.py --model llama3.1:8b "hello"
        """,
    )

    parser.add_argument(
        "message",
        nargs="?",
        help="Natural language message for the agent",
    )
    parser.add_argument(
        "--agent", "-a",
        default="architect",
        help="Name of the agent to invoke (default: architect)",
    )
    parser.add_argument(
        "--model", "-m",
        default=DEFAULT_MODEL,
        help="LLM model to use (default: defined in .env)",
    )
    parser.add_argument(
        "--interactive", "-i",
        action="store_true",
        help="Interactive mode (conversation loop)",
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
