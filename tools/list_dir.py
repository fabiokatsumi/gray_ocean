"""
list_dir — Lists the content of a directory in Gray Ocean.

Unix analog: ls
Input: path (str) — path relative to the gray_ocean root (default: ".")
Output: formatted list of files and directories

Usage example:
    result = run(path="tools")
    result = run(path="agents")
"""

import os

TOOL_NAME = "list_dir"
TOOL_DESCRIPTION = "Lists the content of a directory. Receives 'path' (relative path, default: gray_ocean root)."
TOOL_PARAMETERS = {
    "path": "Relative path to the directory (default: '.')"
}

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def run(path: str = ".") -> str:
    """Lists files and directories at the specified path."""
    full_path = os.path.join(BASE_DIR, path)
    full_path = os.path.normpath(full_path)

    # Security: do not allow traversal outside gray_ocean
    if not full_path.startswith(BASE_DIR):
        return f"ERROR: Access denied. Path '{path}' is outside gray_ocean."

    if not os.path.exists(full_path):
        return f"ERROR: Directory not found: {path}"

    if not os.path.isdir(full_path):
        return f"ERROR: '{path}' is not a directory. Use read_file for files."

    try:
        entries = sorted(os.listdir(full_path))
        if not entries:
            return f"Directory '{path}' is empty."

        lines = []
        for entry in entries:
            entry_path = os.path.join(full_path, entry)
            if os.path.isdir(entry_path):
                lines.append(f"  [DIR]  {entry}/")
            else:
                size = os.path.getsize(entry_path)
                lines.append(f"  [FILE] {entry} ({size} bytes)")

        header = f"Contents of '{path}':\n"
        return header + "\n".join(lines)
    except Exception as e:
        return f"ERROR listing '{path}': {e}"
