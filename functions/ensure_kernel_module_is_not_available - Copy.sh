#!/usr/bin/env bash

check_kernel_module() {
    local l_mod_name="${1}"
    local l_mod_type="${2:-fs}"
    found=false
    if [ -z "$l_mod_name" ]; then
        # echo "Error: Module name required"
        # return 1 # <-- FIX: Changed from 'return false'
        return 1
    fi
    
    while IFS= read -r l_mod_path; do
        if [ -d "$l_mod_path/${l_mod_name/-/\/}" ] && [ -n "$(ls -A "$l_mod_path/${l_mod_name/-/\/}")" ]; then
            found=true
            break
        fi
    done < <(readlink -f /usr/lib/modules/**/kernel/$l_mod_type 2>/dev/null || readlink -f /lib/modules/**/kernel/$l_mod_type 2>/dev/null)

    if [ "$found" = true ]; then
        # echo "$l_mod_name: FAIL (module present)"
        # return 1  # <-- FIX: Changed from 'return false'
        return 1
    else
        # echo "$l_mod_name: PASS (module not present)"
        # return 0  # <-- FIX: Changed from 'return true'
        return 0
    fi
}

# Added the function call to execute the script's logic
check_kernel_module "$@"