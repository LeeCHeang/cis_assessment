#!/bin/usr/env bash

check_dpkg_installation(){
    dpkg_name="$1"
    check_type="${2:-not_installed}"
    if [ -z "$dpkg_name" ]; then
        echo "Error: Package name required"
        return 1
    fi

    if dpkg-query -s "$dpkg_name" &>/dev/null; then
        if [ "$check_type" = "installed" ]; then
            echo "Passed: \"$dpkg_name\" is installed"
            return 0
        else
            echo "Failed: \"$dpkg_name\" is installed"
            return 1
        fi
    else
        if [ "$check_type" = "installed" ]; then
            echo "Failed: \"$dpkg_name\" is not installed"
            return 1
        else
            echo "Passed: \"$dpkg_name\" is not installed"
            return 0
        fi
    fi
}

# --- THIS IS THE FIX ---
# This line calls the function defined above and passes all command-line
# arguments ($@) to it.
check_dpkg_installation "$@"