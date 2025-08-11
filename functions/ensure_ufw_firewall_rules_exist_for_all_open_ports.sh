#!/usr/bin/env bash

{
  unset a_ufwout
  unset a_openports

  # Read UFW Ports
  while read -r l_ufwport; do
    [ -n "$l_ufwport" ] && a_ufwout+=("$l_ufwport")
  done < <(ufw show raw 2>&1 |grep -Po 'dpt:\K\d+' |sort -u)

    # Read Multiport Rules
  while read -r l_multiport; do
    for port in $(echo "$l_multiport" | awk -F'--dports ' '{print $2}' | awk -F' ' '{print $1}' | tr ',' '\n'); do
      if [[ "$port" == *:* ]]; then
        IFS=':' read -r start_port end_port <<< "$port"
        for ((i=start_port; i<=end_port; i++)); do
          a_ufwout+=("$i")
        done
      else    
      a_ufwout+=("$port")
      fi
    done
  done < /etc/ufw/user.rules

  # Read Open Ports
  while read -r l_openport; do
    [ -n "$l_openport" ] && a_openports+=("$l_openport")
  done < <(ss -tuln | awk '($5!~/%lo:/ && $5!~/^127\./ && $5!~/\[?::1\]?:/) {split($5, a, ":"); print a[2]}' | sort -u)

  # Find Differences
  a_diff=("$(printf '%s\n' "${a_openports[@]}" "${a_ufwout[@]}" "${a_ufwout[@]}" | sort | uniq -u)")

  # Conditional Check and Output
  if [[ -n "${a_diff[*]}" ]]; then
    echo -e "\n- Audit Result:\n ** FAIL **\n- The following port(s) don't have a rule in UFW: $(printf '%s\n' \\n"${a_diff[*]}")\n- End List"
  else
    echo -e "\n - Audit Passed -\n- All open ports have a rule in UFW\n"
  fi
}