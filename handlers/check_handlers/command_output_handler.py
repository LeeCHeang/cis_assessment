import subprocess
from typing import Dict

# from utils.decorators import debug_wrapper
from utils.execution_utils import execute_command

# @debug_wrapper
def handle(target: str, params: dict) -> Dict[str,any]:
    if params is None:
        params = {}
    # command_to_run = ['/bin/bash', '-c', target]
    try:
        result = execute_command(
            # command_to_run,
            [target],
            # shell=True,
            capture_output=True,
            text=True,
            check=False
        )
        return {
            "stdout": result.stdout.strip(),
            "stderr": result.stderr.strip(),
            "exit_code": result.returncode
        }
    except Exception as e:
        return {"stdout": "", "stderr": f"ERROR: Command failed to execute. Reason: {e}", "exit_code": 127}