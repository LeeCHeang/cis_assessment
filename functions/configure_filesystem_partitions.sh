# Generic function to check if a mount point exists
check_mount_exists() {
    # This function already uses return 0 and 1 correctly. No changes needed.
    local mount_point="$1"
    
    if [ -z "$mount_point" ]; then
        echo "Error: Mount point required"
        return 1
    fi
    
    local output=""
    output=$(findmnt -kn "$mount_point" 2>/dev/null)
    
    if [ -n "$output" ]; then
        echo "PASSED: $mount_point is mounted as separate partition"
        echo "Mount info: $output"
        return 0
    else
        echo "FAILED: $mount_point is not a separate partition"
        return 1
    fi
}

check_mount_option() {

    local mount_point="$1"
    local option="$2"
    local check_type="${3:-present}"
    
    if [ -z "$mount_point" ] || [ -z "$option" ]; then
        echo "Error: Mount point and option required"
        return 1 # <-- FIX: Changed from 'return false'
    fi
    
    local mount_info=""
    mount_info=$(findmnt -kn "$mount_point" 2>/dev/null)
    
    if [ -z "$mount_info" ]; then
        echo "FAILED: $mount_point partition not found"
        return 1 # <-- FIX: Changed from 'return false'
    fi
    
    if [ "$check_type" = "present" ]; then
        local check_result=""
        check_result=$(echo "$mount_info" | grep -v "$option")
        
        if [ -z "$check_result" ]; then
            echo "PASSED: $option option is set on $mount_point"
            return 0 # <-- FIX: Changed from 'return true'
        else
            echo "FAILED: $option option is NOT set on $mount_point"
            echo "Current mount: $mount_info"
            return 1 # <-- FIX: Changed from 'return false'
        fi
    else
        local check_result=""
        check_result=$(echo "$mount_info" | grep "$option")
        
        if [ -z "$check_result" ]; then
            echo "PASSED: $option option is NOT set on $mount_point"
            return 0 # <-- FIX: Changed from 'return true'
        else
            echo "FAILED: $option option IS set on $mount_point (should not be)"
            echo "Current mount: $mount_info"
            return 1 # <-- FIX: Changed from 'return false'
        fi
    fi
}

# NOTE: This script defines two functions. You need to decide which one to call,
# or create separate scripts for each function to be called by the audit handler.
# For now, no function is called by default.