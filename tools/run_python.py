"""
run_python — Executes Python code in a sandbox.

Unix analog: exec / subprocess
Input: code (str) — Python code to be executed
Output: stdout + stderr from execution

Usage example:
    result = run(code="print(2 + 2)")
"""

import subprocess
import sys
import tempfile
import os

TOOL_NAME = "run_python"
TOOL_DESCRIPTION = "Executes Python code in a sandbox. Receives 'code' (Python code to execute)."
TOOL_PARAMETERS = {
    "code": "Python code to be executed"
}

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def run(code: str) -> str:
    """Executes Python code in an isolated subprocess."""
    try:
        # Write the code to a temporary file
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".py", delete=False, encoding="utf-8"
        ) as f:
            f.write(code)
            tmp_path = f.name

        try:
            result = subprocess.run(
                [sys.executable, tmp_path],
                capture_output=True,
                text=True,
                timeout=30,
                cwd=BASE_DIR,
            )

            output = ""
            if result.stdout:
                output += result.stdout
            if result.stderr:
                if output:
                    output += "\n--- STDERR ---\n"
                output += result.stderr

            if result.returncode != 0:
                output = f"ERROR (exit code {result.returncode}):\n{output}"
            elif not output:
                output = "OK: Code executed with no output."

            return output

        finally:
            os.unlink(tmp_path)

    except subprocess.TimeoutExpired:
        return "ERROR: Timeout — execution exceeded 30 seconds."
    except Exception as e:
        return f"ERROR executing code: {e}"
