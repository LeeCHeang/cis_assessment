#!/usr/bin/env bash
{
    # Check if systemd-coredump is installed
    coredump_is_install=$(systemctl list-unit-files | grep coredump)
    
    # Check configuration settings in the actual config file
    storage=$(grep -Psi -- '^\s*Storage\s*=\s*none\s*$' /etc/systemd/coredump.conf)
    processSize=$(grep -Psi -- '^\s*ProcessSizeMax\s*=\s*0' /etc/systemd/coredump.conf)
    
    # For testing with test file (comment out the lines above and uncomment these):
    # storage=$(grep -Psi -- '^\s*Storage\s*=\s*none\s*$' ~/Documents/grep.txt)
    # processSize=$(grep -Psi -- '^\s*ProcessSizeMax\s*=\s*0' ~/Documents/grep.txt)
    
    overall_pass=true
    
    if [ -n "$coredump_is_install" ]; then
        echo "systemd-coredump is installed, checking configuration..."
        
        if [ -z "$storage" ]; then
            echo "** FAIL ** - Storage is not set to 'none'"
            overall_pass=false
        fi
        
        if [ -z "$processSize" ]; then
            echo "** FAIL ** - ProcessSizeMax is not set to '0'"
            overall_pass=false
        fi
        
        if [ -n "$storage" ] && [ -n "$processSize" ]; then
            echo "Both Storage and ProcessSizeMax are correctly configured"
        fi
    else
        echo "systemd-coredump is not installed - no configuration needed"
        overall_pass=true
    fi
    
    if [ "$overall_pass" = true ]; then
        echo "** PASS **"
        exit 0
    else
        echo "** FAIL **"
        exit 1
    fi
}