import subprocess
import re
from typing import Dict, Optional
from utils.remote_utils import RemoteExecutor

# variable to hold remote executor when doing remote audits
remo_runner: Optional[RemoteExecutor] = None

# def reformat_output(output: str) -> str:
#     if not output:
#         return ""
#     cleaned = output.replace('\\n', '\n')
#     cleaned = re.sub(r'\s+', ' ', cleaned)
    
#     return cleaned.strip()

def set_remote_executor(executor: RemoteExecutor):
    global remo_runner
    remo_runner = executor

def cls_remo_runner():
    global remo_runner
    remo_runner = None

def call_remo_runner() -> Optional[RemoteExecutor]:
    global remo_runner
    return remo_runner

def switch_mode() -> bool:
    global remo_runner
    return remo_runner is not None

def execute_command(command, shell=True, capture_output=True, text=True, check=False) -> subprocess.CompletedProcess:
    global remo_runner
    
    if remo_runner is None:
        if isinstance(command, list):
            result = subprocess.run(command, shell=shell, capture_output=capture_output, text=text, check=check)
        else:
            result = subprocess.run(command, shell=shell, capture_output=capture_output, text=text, check=check)
        
        # result.stdout = reformat_output(result.stdout) if result.stdout else ""
        # result.stderr = reformat_output(result.stderr) if result.stderr else ""
        return result
    else:
        if isinstance(command, list):
            if command[0] == '/bin/bash' and command[1] == '-c' and len(command) == 3:
                command_str = command[2]  # Extract the actual command
            else:
                command_str = ' '.join(command)
        else:
            command_str = command
        
        try:
            if not command_str.strip().startswith('sudo'):
                command_str = f"sudo {command_str}"
            
            stdout, stderr = remo_runner.run_command(command_str)
            
            # stdout = reformat_output(stdout)
            # stderr = reformat_output(stderr)
            
            class ShellOutput:
                def __init__(self, stdout, stderr, returncode):
                    self.stdout = stdout
                    self.stderr = stderr
                    self.returncode = returncode
            
            returncode = 0 if not stderr else 1
            
            return ShellOutput(stdout, stderr, returncode)
            
        except Exception as e:
            class ShellOutput:
                def __init__(self, stdout, stderr, returncode):
                    self.stdout = stdout
                    self.stderr = stderr
                    self.returncode = returncode
            
            return ShellOutput("", f"Remote execution error: {e}", 127)
