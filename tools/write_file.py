"""
write_file — Creates or overwrites a file in Gray Ocean.

Unix analog: echo >
Input: path (str) — path relative to the gray_ocean root
       content (str) — content to be written
Output: confirmation or error

Usage example:
    result = run(path="tools/new_tool.py", content="def run(): ...")
"""

import os

TOOL_NAME = "write_file"
TOOL_DESCRIPTION = "Creates or overwrites a file. Receives 'path' (relative path) and 'content' (content to write)."
TOOL_PARAMETERS = {
    "path": "Relative path to the file to be created/overwritten",
    "content": "Content to be written to the file"
}

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def run(path: str, content: str) -> str:
    """Creates or overwrites a file with the provided content."""
    full_path = os.path.join(BASE_DIR, path)
    full_path = os.path.normpath(full_path)

    # Security: do not allow traversal outside gray_ocean
    if not full_path.startswith(BASE_DIR):
        return f"ERROR: Access denied. Path '{path}' is outside gray_ocean."

    try:
        # Create intermediate directories if needed
        dir_path = os.path.dirname(full_path)
        if dir_path and not os.path.exists(dir_path):
            os.makedirs(dir_path, exist_ok=True)

        with open(full_path, "w", encoding="utf-8") as f:
            f.write(content)

        return f"OK: File '{path}' written successfully ({len(content)} characters)."
    except Exception as e:
        return f"ERROR writing '{path}': {e}"
