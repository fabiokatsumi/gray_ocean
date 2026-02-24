"""
read_file — Reads the content of a file in Gray Ocean.

Unix analog: cat
Input: path (str) — path relative to the gray_ocean root
Output: file content as string

Usage example:
    result = run(path="tools/index.md")
"""

import os

TOOL_NAME = "read_file"
TOOL_DESCRIPTION = "Reads the content of a file. Receives 'path' (path relative to the gray_ocean root)."
TOOL_PARAMETERS = {
    "path": "Relative path to the file to be read"
}

# Gray Ocean root (parent directory of tools/)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def run(path: str) -> str:
    """Reads and returns the content of a file."""
    full_path = os.path.join(BASE_DIR, path)
    full_path = os.path.normpath(full_path)

    # Security: do not allow traversal outside gray_ocean
    if not full_path.startswith(BASE_DIR):
        return f"ERROR: Access denied. Path '{path}' is outside gray_ocean."

    if not os.path.exists(full_path):
        return f"ERROR: File not found: {path}"

    if not os.path.isfile(full_path):
        return f"ERROR: '{path}' is not a file. Use list_dir for directories."

    try:
        with open(full_path, "r", encoding="utf-8") as f:
            content = f.read()
        return content
    except Exception as e:
        return f"ERROR reading '{path}': {e}"
