import os

def check_config_file(target_file: str, params: dict) -> str:
    key = params.get('key')
    expected_value = params.get('expected_value')

    if not all([key, expected_value]):
        return "ERROR: Missing 'key' or 'expected_value' in parameters"

    if not os.path.exists(target_file):
        return f"FAILED: Config file '{target_file}' not found."

    try:
        with open(target_file, 'r') as f:
            for line in f:
                clean_line = line.strip()
                if not clean_line or clean_line.startswith('#'):
                    continue
                
                parts = clean_line.split()
                if len(parts) >= 2 and parts[0].lower() == key.lower() and parts[1].lower() == expected_value.lower():
                    return f"PASSED: Found '{key} {expected_value}' in {target_file}"
        
        return f"FAILED: Did not find '{key} {expected_value}' in {target_file}"

    except Exception as e:
        return f"ERROR: Could not read file '{target_file}'. Reason: {e}"
