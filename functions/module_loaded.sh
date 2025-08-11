#!/usr/bin/env bash
module_loadable()
{
    module_name="$1" 
    
    # Check if module is currently loaded
    if lsmod | grep -q "^$module_name\s"; then
        echo "FAILED: Module '$module_name' is currently loaded."
        return 1
    fi

    # Module is not loaded, now check if it's loadable or truly absent
    output=$(modprobe -n -v "$module_name" 2>&1)
    
    # Case 1: The module is completely unavailable. This is a PASS.
    if echo "$output" | grep -q "FATAL: Module .* not found"; then
        echo "PASSED: Module '$module_name' is not found, as desired."
        return 0
    
    # Case 2: The module is present but explicitly disabled. This is a PASS.
    elif echo "$output" | grep -Eq "^\s*install\s+\/bin\/(true|false)\b"; then
        echo "PASSED: Module '$module_name' is disabled ($output)."
        return 0
        
    # Case 3: The module is present and loadable. This is a FAIL.
    else
        echo "FAILED: Module '$module_name' appears to be loadable."
        return 1
    fi
}

module_loadable "$@"