"""
register_tool — Registers a new tool in Gray Ocean.

Unix analog: install
Input: name (str) — tool name (without .py)
       code (str) — Python code for the tool (must have a run() function)
       description (str) — short description of the tool
Output: confirmation or error

Usage example:
    result = run(
        name="fibonacci",
        code="def run(n: int) -> str:\\n    ...",
        description="Calculates the n-th Fibonacci number"
    )
"""

import os
from datetime import datetime

TOOL_NAME = "register_tool"
TOOL_DESCRIPTION = "Registers a new tool in gray ocean. Receives 'name' (name), 'code' (Python code with run()) and 'description' (description)."
TOOL_PARAMETERS = {
    "name": "Tool name (without .py extension)",
    "code": "Python code for the tool (must contain a run() function)",
    "description": "Short description of what the tool does"
}

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOOLS_DIR = os.path.join(BASE_DIR, "tools")
INDEX_PATH = os.path.join(TOOLS_DIR, "index.md")


def run(name: str, code: str, description: str) -> str:
    """Saves a new tool as .py and updates index.md."""
    # Name validation
    if not name.isidentifier():
        return f"ERROR: Name '{name}' is invalid. Use only letters, numbers and underscores."

    # Check if already exists
    tool_path = os.path.join(TOOLS_DIR, f"{name}.py")
    if os.path.exists(tool_path):
        return f"ERROR: Tool '{name}' already exists. Edit the file directly if you want to modify it."

    # Check if the code contains a run() function
    if "def run(" not in code:
        return "ERROR: The code must contain a run() function. Pattern: def run(...) -> str:"

    try:
        # Save the tool file
        with open(tool_path, "w", encoding="utf-8") as f:
            f.write(code)

        # Update index.md
        today = datetime.now().strftime("%Y-%m-%d")
        entry = f"\n### `{name}`\n- **File:** `tools/{name}.py`\n- **Description:** {description}\n- **Registered on:** {today}\n- **Origin:** created by agent\n"

        with open(INDEX_PATH, "a", encoding="utf-8") as f:
            f.write(entry)

        return f"OK: Tool '{name}' registered successfully in tools/{name}.py and added to index.md."

    except Exception as e:
        # Clean up on partial error
        if os.path.exists(tool_path):
            os.unlink(tool_path)
        return f"ERROR registering tool '{name}': {e}"
