import os, subprocess
from typing import List, Dict
# from utils.decorators import debug_wrapper
from utils.execution_utils import execute_command, switch_mode, call_remo_runner
import tempfile
import uuid

# @debug_wrapper
def handle(script_name: str, params: List[str]) -> Dict[str, any]:  # Fixed return type
    if not script_name:
        return {
            'stdout': '',
            'stderr': 'ERROR: No script name provided.',
            'exit_code': 1
        }
    
    script_path = os.path.abspath(f"functions/{script_name}")
    if not isinstance(params, list):
        params = []
    
    if switch_mode():
        return remo_script(script_path, params)
    else:
        return local_script(script_path, params)

def local_script(script_path: str, params: List[str]) -> Dict[str, any]:
    script_command = ['bash', script_path] + params
    
    try:
        result = execute_command(
            script_command, 
            capture_output=True, 
            text=True, 
            check=False
        )
        return {
            'stdout': result.stdout.strip(),
            'stderr': result.stderr.strip(),
            'exit_code': result.returncode
        }
    except FileNotFoundError:
        return {
            'stdout': '',
            'stderr': f"ERROR: 'bash' or script '{script_path}' not found.",
            'exit_code': 1
        }
    except Exception as e:
        return {
            'stdout': '',
            'stderr': f"ERROR: An unexpected exception occurred: {e}",
            'exit_code': 1
        }

def remo_script(script_path: str, params: List[str]) -> Dict[str, any]:
    try:
        if not os.path.exists(script_path):
            return {
                'stdout': '',
                'stderr': f"ERROR: Local script '{script_path}' not found.",
                'exit_code': 1
            }
        
        with open(script_path, 'r') as f:
            script_content = f.read()
        
        remote_script_path = f"/tmp/audit_script_{uuid.uuid4().hex[:8]}.sh"
        
        executor = call_remo_runner()
        if not executor.upload_script_content(script_content, remote_script_path):
            return {
                'stdout': '',
                'stderr': f"ERROR: Failed to upload script to remote server.",
                'exit_code': 1
            }
        
        try:
            script_command = ['sudo', 'bash', remote_script_path] + params
            result = execute_command(
                script_command, 
                capture_output=True, 
                text=True, 
                check=False
            )
            
            return_value = {
                'stdout': result.stdout.strip(),
                'stderr': result.stderr.strip(),
                'exit_code': result.returncode
            }
            
        finally:
            try:
                # This work for now and also very dangerous
                executor.run_command(f"sudo rm -f {remote_script_path}")
            except:
                pass  # Ignore cleanup errors
                
        return return_value
        
    except Exception as e:
        return {
            'stdout': '',
            'stderr': f"ERROR: Remote script execution failed: {e}",
            'exit_code': 1
        }