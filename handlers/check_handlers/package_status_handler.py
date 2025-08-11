import subprocess
from utils.execution_utils import execute_command

# from utils.decorators import debug_wrapper # <-- Import our new decorator

# @debug_wrapper # <-- Apply the decorator to the handle function
def handle(target: str, params: dict) -> str:
    if not target:
        return {
            "stdout": '',
            "stderr": 'Error Not Package Have input',
            "exit_code": 1
        }
    try:
        result = execute_command(['dpkg-query', '-s', target], capture_output=True, text=True)
        # return "installed" if result.returncode == 0 else "not_installed"
        return {
            "stdout": result.stdout.strip(),
            "stderr": result.stderr.strip(),
            "exit_code": result.returncode
        }

    except FileNotFoundError as e:
        # return "ERROR: dpkg-query not found."
        return { 
                'stdout':"",
                'stderr':"ERROR: dpkg-query not found. {e}",
                'exit_code': 1,
        }

    except Exception as e:
        return {"stdout": "", "stderr": f"ERROR: Command failed to execute. Reason: {e}", "exit_code": 127}