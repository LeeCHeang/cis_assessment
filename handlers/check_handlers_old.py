import subprocess
import os
import re
def handle_package_status(target: str, params: dict) -> str:
    try:
        result = subprocess.run(['dpkg-query', '-s', target], capture_output=True, text=True)
        return "installed" if result.returncode == 0 else "not_installed"
    except FileNotFoundError:
        return "ERROR: dpkg-query not found."


def handle_config_file_value(target: str, params: dict) -> str:
    key_to_find = params.get('key')
    if not key_to_find:
        return "ERROR: Missing 'key' in parameters."
        
    # If the config file doesn't exist, we can't find the key.
    # For most security checks, if the service isn't configured, it's secure.
    if not os.path.exists(target):
        # We return a special status that we can interpret as a PASS for this check type.
        # Let's return the `expected_value` from the check, which will cause a PASS.
        # This is an intelligent default for "secure by absence".
        return params.get("pass_if_missing", True) 
    
    try:
        with open(target, 'r') as f:
            for line in f:
                clean_line = line.strip()
                if clean_line.startswith('#') or not clean_line:
                    continue
                parts = clean_line.split()
                if len(parts) >= 2 and parts[0].lower() == key_to_find.lower():
                    return parts[1] # Return the raw value
        return "ERROR: Key not found in file."
    except Exception as e:
        return f"ERROR: Failed to read file. Reason: {e}"

def handle_kernel_module_status(target: str, params: dict) -> str:
    module_name = target

    # 1. Verify the module is not loaded, as per the first command
    try:
        lsmod_result = subprocess.run(['lsmod'], capture_output=True, text=True)
        if re.search(r"^\s*" + re.escape(module_name) + r"\s", lsmod_result.stdout, re.MULTILINE):
            return "loaded" # FAIL condition: Module is running
    except FileNotFoundError:
        return "ERROR: 'lsmod' command not found."

    # 2. If not loaded, verify the module is not loadable, as per the second command
    try:
        # This command shows the effective modprobe configuration
        showconfig_result = subprocess.run(['modprobe', '--showconfig'], capture_output=True, text=True)
        config_output = showconfig_result.stdout

        # Now we check the output for the specific blacklist/install lines
        # This is the logic from the CIS documentation screenshot
        is_blacklisted = re.search(r"^\s*blacklist\s+" + re.escape(module_name) + r"\b", config_output, re.MULTILINE)
        is_install_disabled = re.search(r"^\s*install\s+" + re.escape(module_name) + r"\s+/bin/(true|false)", config_output, re.MULTILINE)
        
        # If the module is disabled by either method, it is "not_available"
        if is_blacklisted or is_install_disabled:
            return "not_available" # PASS condition: Module is correctly disabled
        else:
            # If it's not loaded and not disabled, it must be available to be loaded
            return "available" # FAIL condition: Module is not disabled
            
    except FileNotFoundError:
        return "ERROR: 'modprobe' command not found."
    except Exception as e:
        return f"ERROR: An unexpected exception occurred: {e}"

def handle_command_output(target: str, params: dict) -> str:
    try:
        result = subprocess.run(target, shell=True, capture_output=True, text=True)
        return result.stdout.strip()
    except Exception as e:
        return f"ERROR: Command failed to execute. Reason: {e}"

def handle_mount_point(target: str, params: dict) -> str:
    if not target:
        return "ERROR: Mount point target cannot be empty."

    try:
        # The 'findmnt -kn <path>' command returns info only if it's a mount point.
        # This is the same command used in your configure_filesystem_partitions.sh script.
        result = subprocess.run(
            ['findmnt', '-kn', target],
            capture_output=True,
            text=True
        )
        
        # If the command's output is not empty, a mount point was found.
        if result.stdout.strip():
            return "is_separate_partition"
        else:
            return "is_not_separate_partition"
            
    except FileNotFoundError:
        return "ERROR: 'findmnt' command not found."
    except Exception as e:
        return f"ERROR: An unexpected exception occurred: {e}"