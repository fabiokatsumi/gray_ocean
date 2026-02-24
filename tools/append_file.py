"""
append_file — Appends content to the end of an existing file.

Unix analog: echo >>
Input: path (str) — path relative to the gray_ocean root
       content (str) — content to be appended
Output: confirmation or error

Usage example:
    result = run(path="agents/architect/log.md", content="\n## Action 1\n...")
"""

import os

TOOL_NAME = "append_file"
TOOL_DESCRIPTION = "Appends content to the end of a file. Receives 'path' (relative path) and 'content' (content to append)."
TOOL_PARAMETERS = {
    "path": "Relative path to the file",
    "content": "Content to be appended to the end of the file"
}

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def run(path: str, content: str) -> str:
    """Appends content to the end of a file."""
    full_path = os.path.join(BASE_DIR, path)
    full_path = os.path.normpath(full_path)

    # Security: do not allow traversal outside gray_ocean
    if not full_path.startswith(BASE_DIR):
        return f"ERROR: Access denied. Path '{path}' is outside gray_ocean."

    if not os.path.exists(full_path):
        return f"ERROR: File not found: {path}. Use write_file to create it."

    try:
        with open(full_path, "a", encoding="utf-8") as f:
            f.write(content)

        return f"OK: Content appended to '{path}' ({len(content)} characters)."
    except Exception as e:
        return f"ERROR appending to '{path}': {e}"
