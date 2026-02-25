#!/usr/bin/env python3
"""
live.py — Gray Ocean Live Loop

Runs the Architect (or any agent) on a repeating heartbeat, giving it
periodic prompts to review the system state and take one incremental
improvement step autonomously.

Usage:
    python live.py                        # Architect every 5 minutes
    python live.py --interval 10          # every 10 minutes
    python live.py --once                 # run once and exit
    python live.py --agent architect --prompt "Review all tools and improve one"
    python live.py --model llama3.1:70b   # use a specific model
"""

import sys
import os
import time
import argparse
import signal
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

DEFAULT_INTERVAL_MINUTES = 5

DEFAULT_PROMPT = (
    "Review the current state of the Gray Ocean system. "
    "Check what tools exist (tools/index.md), what agents exist (agents/), "
    "and what improvements are pending (gray_ocean_ideas/pending_ideas.md). "
    "Pick the single most valuable missing piece and build it. "
    "If everything looks complete, pick the most impactful improvement and make it. "
    "Follow VALUES.md at all times. Do one thing well."
)


def clear_runtime_caches():
    """
    Clears all in-memory caches so each cycle re-reads fresh state from disk.
    This is necessary because the Architect may create new tools/agents during a
    cycle, and those changes must be visible to the next cycle.
    """
    import core.runtime as rt
    rt._agent_cache.clear()
    rt._tool_module_cache.clear()
    rt._system_prompt_cache.clear()
    rt._values_cache = None


def run_cycle(agent: str, prompt: str, model: str, cycle_number: int):
    """Runs a single agent cycle."""
    from core.runtime import run_agent

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    separator = "=" * 60
    print(f"\n{separator}")
    print(f"  CYCLE #{cycle_number} — {timestamp}")
    print(f"  Agent : {agent}")
    print(f"  Model : {model}")
    print(f"{separator}\n")

    clear_runtime_caches()

    try:
        run_agent(agent, prompt, model=model)
    except FileNotFoundError as e:
        print(f"\n  ERROR: Agent not found — {e}", file=sys.stderr)
    except Exception as e:
        print(f"\n  ERROR in cycle #{cycle_number}: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()


def load_default_model() -> str:
    """Reads the default model from .env."""
    env_path = os.path.join(BASE_DIR, ".env")
    if not os.path.exists(env_path):
        return "llama3.1:8b"
    env = {}
    with open(env_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                env[k.strip()] = v.strip()
    return (
        env.get("OLLAMA_MODEL")
        or env.get("OPENAI_MODEL")
        or env.get("OPENROUTER_MODEL")
        or "llama3.1:8b"
    )


def main():
    parser = argparse.ArgumentParser(
        description="Gray Ocean Live Loop — keeps an agent running autonomously",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python live.py                         # Architect every 5 minutes
  python live.py --interval 15           # every 15 minutes
  python live.py --once                  # run once and exit (great for testing)
  python live.py --agent architect --prompt "Build the Router agent"
  python live.py --model llama3.1:70b    # use a stronger model
        """,
    )
    parser.add_argument(
        "--interval", "-n",
        type=float,
        default=DEFAULT_INTERVAL_MINUTES,
        metavar="MINUTES",
        help=f"Minutes between cycles (default: {DEFAULT_INTERVAL_MINUTES})",
    )
    parser.add_argument(
        "--agent", "-a",
        default="architect",
        help="Agent to invoke each cycle (default: architect)",
    )
    parser.add_argument(
        "--model", "-m",
        default=None,
        help="LLM model to use (default: from .env)",
    )
    parser.add_argument(
        "--prompt", "-p",
        default=DEFAULT_PROMPT,
        help="Heartbeat prompt sent to the agent each cycle",
    )
    parser.add_argument(
        "--once",
        action="store_true",
        help="Run a single cycle then exit (useful for cron or manual triggering)",
    )

    args = parser.parse_args()

    if args.model is None:
        args.model = load_default_model()

    interval_seconds = args.interval * 60

    # Graceful shutdown: finish the current cycle before stopping
    running = [True]

    def handle_sigint(sig, frame):
        print("\n\n  Ctrl+C received — finishing current cycle then stopping...\n")
        running[0] = False

    signal.signal(signal.SIGINT, handle_sigint)

    mode_label = "single run (--once)" if args.once else f"every {args.interval} min"
    print(f"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
   GRAY OCEAN — Live Loop
   Agent   : {args.agent}
   Model   : {args.model}
   Mode    : {mode_label}
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Press Ctrl+C to stop after the current cycle completes.
""")

    cycle = 0
    while running[0]:
        cycle += 1
        run_cycle(args.agent, args.prompt, args.model, cycle)

        if args.once or not running[0]:
            break

        next_run = datetime.fromtimestamp(time.time() + interval_seconds)
        print(
            f"\n  Sleeping until {next_run.strftime('%H:%M:%S')} "
            f"({args.interval} min). Ctrl+C to stop.\n"
        )

        # Sleep in 1-second increments so Ctrl+C is always responsive
        deadline = time.time() + interval_seconds
        while time.time() < deadline and running[0]:
            time.sleep(1)

    print("\n  Gray Ocean live loop stopped.\n")


if __name__ == "__main__":
    main()
