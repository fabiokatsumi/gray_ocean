"""
send_message — Pipes a message to another agent and returns its response.

Unix analog: pipe (|)
Input: to (str) — target agent name
       message (str) — the message to send
Output: target agent's response

Usage example:
    result = run(to="my_chat_bot", message="What tools do you have access to?")
"""

import os
from datetime import datetime

# Recursion guard: reject pipe chains deeper than this
MAX_PIPE_DEPTH = 3
_pipe_depth = 0

TOOL_NAME = "send_message"
TOOL_DESCRIPTION = "Sends a message to another agent and returns its response. Like a pipe: your message becomes the other agent's input. All traffic is logged to messages.md."
TOOL_PARAMETERS = {
    "to": "Target agent name (must exist under agents/)",
    "message": "The message to send to the agent",
}

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AGENTS_DIR = os.path.join(BASE_DIR, "agents")
MESSAGES_PATH = os.path.join(BASE_DIR, "messages.md")

MESSAGES_HEADER = """# Messages — Gray Ocean

> Append-only log of all inter-agent pipe traffic.
> Automatically updated by the `send_message` tool.

---
"""


def _ensure_messages_file():
    """Create messages.md with header if it does not exist."""
    if not os.path.exists(MESSAGES_PATH):
        with open(MESSAGES_PATH, "w", encoding="utf-8") as f:
            f.write(MESSAGES_HEADER)


def _log_exchange(to: str, message: str, response: str):
    """Append one pipe exchange to messages.md."""
    _ensure_messages_file()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    summary = response[:300] + "..." if len(response) > 300 else response
    summary = summary.replace("\n", " ")
    entry = f"""
## {timestamp} — pipe → {to}

**Message:** {message[:200]}{"..." if len(message) > 200 else ""}

**Response:** {summary}

---
"""
    with open(MESSAGES_PATH, "a", encoding="utf-8") as f:
        f.write(entry)


def run(to: str, message: str) -> str:
    """Sends the message to the target agent and returns its response."""
    global _pipe_depth

    to_safe = to.lower().strip()
    agent_dir = os.path.join(AGENTS_DIR, to_safe)
    if not os.path.isdir(agent_dir):
        return f"ERROR: Agent '{to}' not found. Check agents/ for valid names."

    if _pipe_depth >= MAX_PIPE_DEPTH:
        return (
            f"ERROR: Pipe depth limit ({MAX_PIPE_DEPTH}) reached. "
            "Avoid piping agent → agent → agent → agent."
        )

    _pipe_depth += 1
    try:
        from core.runtime import run_agent

        response = run_agent(to_safe, message)
        _log_exchange(to_safe, message, response)
        return response
    finally:
        _pipe_depth -= 1
