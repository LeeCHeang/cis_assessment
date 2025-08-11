import subprocess
import re
from utils.execution_utils import execute_command

def handle(target: str, params: dict) -> str:
    module_name = target

    # # 1. Verify the module is not loaded, as per the first command
    try:
        lsmod_result = execute_command(['lsmod'], capture_output=True, text=True)
        if re.search(r"^\s*" + re.escape(module_name) + r"\s", lsmod_result.stdout, re.MULTILINE):
            return "loaded" # FAIL condition: Module is running
    except FileNotFoundError:
        return "ERROR: 'lsmod' command not found."

    # 2. If not loaded, verify the module is not loadable, as per the second command
    try:
        showconfig_result = execute_command(['modprobe', '--showconfig'], capture_output=True, text=True)
        config_output = showconfig_result.stdout
        # # Now we check the output for the specific blacklist/install lines
        # This is the logic from the CIS documentation screenshot
        is_blacklisted = re.search(r"^\s*blacklist\s+" + re.escape(module_name) + r"\b", config_output, re.MULTILINE)
        is_install_disabled = re.search(r"^\s*install\s+" + re.escape(module_name) + r"\s+/bin/(true|false)", config_output, re.MULTILINE)
        
        # If the module is disabled by either method, it is "not_available"
        # if is_blacklisted or is_install_disabled:
        #     return "not_available" # PASS condition: Module is correctly disabled
        #     # return {
        #     #     "stdout": showconfig_result.stdout.strip(),
        #     #     "stderr": showconfig_result.stderr.strip(),
        #     #     "exit_code": showconfig_result.returncode
        #     # }
        # else:
        #     # If it's not loaded and not disabled, it must be available to be loaded
        #     return "available" # FAIL condition: Module is not disabled
            
        return {
            "stdout": is_blacklisted.group() if is_blacklisted else (is_install_disabled.group() if is_install_disabled else None),
            "stderr": showconfig_result.stderr.strip(),
            "exit_code": showconfig_result.returncode
        }
    except FileNotFoundError:
        return "ERROR: 'modprobe' command not found."
    except Exception as e:
        return f"ERROR: An unexpected exception occurred: {e}"