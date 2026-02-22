"""
run_python — Executa código Python em sandbox.

Analogia Unix: exec / subprocess
Input: code (str) — código Python a ser executado
Output: stdout + stderr da execução

Exemplo de uso:
    result = run(code="print(2 + 2)")
"""

import subprocess
import sys
import tempfile
import os

TOOL_NAME = "run_python"
TOOL_DESCRIPTION = "Executa código Python em sandbox. Recebe 'code' (código Python a executar)."
TOOL_PARAMETERS = {
    "code": "Código Python a ser executado"
}

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def run(code: str) -> str:
    """Executa código Python em um subprocesso isolado."""
    try:
        # Escreve o código em arquivo temporário
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
                output = f"ERRO (código de saída {result.returncode}):\n{output}"
            elif not output:
                output = "OK: Código executado sem output."

            return output

        finally:
            os.unlink(tmp_path)

    except subprocess.TimeoutExpired:
        return "ERRO: Timeout — execução excedeu 30 segundos."
    except Exception as e:
        return f"ERRO ao executar código: {e}"
