#!/usr/bin/env bash
check_enabled(){
    service_name="$1"
    # If no service name is provided, print an error and return 1
    enabled="" 
    enabled=$(systemctl is-enabled "$service_name" 2>/dev/null | grep '^enabled')
    if [[ -z "$service_name" ]]; then
        echo "Error: check_enable requires a service name." >&2 # Redirect to stderr
        return 1
    fi
    # Check the output and return appropriate exit code
    if [[ "$enabled" == "enabled" ]]; then
        echo "Service '$service_name' is enabled." # Optional: provide user feedback
        return 0 # Success: service is enabled
    else
        echo "Service '$service_name' is NOT enabled (or does not exist)." # Optional: provide user feedback
        return 1 # Failure: service is not enabled or command failed
    fi
}


check_actived(){
    service_name="$1"
    actived=""
    actived=$(systemctl is-active "$service_name" 2>/dev/null | grep '^active')
    # If no service name is provided, print an error and return 1
    if [[ -z "$service_name" ]]; then
        echo "Error: check_actived requires a service name." >&2 # Redirect to stderr
        return 1
    fi
    # Check the output and return appropriate exit code
    if [[ "$actived" == "active" ]]; then
        echo "Service '$service_name' is active." # Optional: provide user feedback
        return 0 # Success: service is active
    else
        echo "Service '$service_name' is NOT active." # Optional: provide user feedback
        return 1 # Failure: service is not active or command failed
    fi

}
check_sysctl() {
    svc="$1"
    check_status="${2:-false}"
    # If no services are provided, print an error and return 1
    if [[ -z "$svc" ]]; then
        echo "Error: check_sysctl requires at least one service name." >&2 # Redirect to stderr
        return 1
    fi 
    # for svc in "${services[@]}"; do

    #     if check_enabled "$svc"; then
    #         echo "Service '$svc' is enabled."
    #     else
    #         echo "Service '$svc' is NOT enabled."
    #     fi

    #     if check_actived "$svc"; then
    #         echo "Service '$svc' is active."
    #     else
    #         echo "Service '$svc' is NOT active."
    #     fi
    # done
    case "$check_status" in
        true|yes|1)
            if check_enabled "$svc" && check_actived "$svc"; then
                echo "Passed - true: Service '$svc' is enabled and active."
                return 0 # Exit with success code if all services are enabled and active
            else
                echo "Failed - true: Service '$svc' is either not enabled or not active."
                return 1 # Exit with error code if any service is not enabled or active
            fi
            ;;
        false|no|0)
            if ! check_enabled "$svc" && ! check_actived "$svc"; then
                echo "Passed - false: Service '$svc' is not enabled and not active."
                return 0 # Exit with success code if all services are not enabled and not active
            else
                echo "Failed - false: Service '$svc' is either enabled or active."
                return 1 # Exit with error code if any service is enabled or active
            fi
            ;;
        *)
            echo "Invalid argument for check_status. Use true/yes/1 or false/no/0." >&2
            return 1 # Exit with error code
            ;;
    esac

}
check_sysctl "$@"