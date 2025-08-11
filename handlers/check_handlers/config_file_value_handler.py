import os
from typing import Dict
def handle(target: str, params: dict) -> Dict[str,any]:
    key_to_find = params.get('key')
    # pass_if_missing_val = params.get('pass_if_missing')
    if not os.path.exists(target):
        # If the file doesn't exist AND we have a 'pass_if_missing' value,
        # return that value. This will cause the check to PASS.
        # if pass_if_missing_val is not None:
        #     return pass_if_missing_val
        # Otherwise, report the error as before.
        return {
            "stdout": '',
            "stderr": f"ERROR: File not found: {target}",
            "error_code": 1
        }
    if not key_to_find:
        # return "ERROR: Missing 'key' in parameters"
        return {
            "stdout": '',
            "stderr": "ERROR: Missing 'key' in parameters",
            "error_code": 1
        }
    
    try:
        with open(target, 'r') as f:
            for line in f:
                # Skip comments and empty lines
                clean_line = line.strip()
                if not clean_line or clean_line.startswith('#'):
                    continue
                
                # Split the line and check for the key.
                # This handles 'key = value', 'key value', 'key: value' etc.
                parts = clean_line.split(None, 1) # Split only on the first whitespace
                if len(parts) == 2 and parts[0].lower() == key_to_find.lower():
                    # Return the raw value, stripping potential quotes
                    print(f"Found key '{key_to_find}': {parts[1]}")
                    return {
                        "stdout": parts[1].strip("'\""),
                        "stderr": '',
                        "exit_code": 0
                    }
                    # return parts[1].strip("'\"")
        
        # return f"ERROR: Key '{key_to_find}' not found in file."
        return {
            "stdout": '',
            "stderr": f"There no '{key_to_find}' found in file.",
            "exit_code": 1 
        }
        
    except Exception as e:
        return { 
            'stdout': "",
            'stderr': f"ERROR: Failed to read file '{target}'. Reason: {e}",
            "exit_code": 2
        }