#!/usr/bin/env bash

{
   a_output=() a_output2=() a_exists2=() a_mode2=() a_owner2=()
   l_valid_shells="^($( awk -F\/ '$NF != "nologin" {print}' /etc/shells | sed -rn '/^\//{s,/,\\\\/,g;p}' | paste -s -d '|' - ))$"
   l_mask='0027'; l_max="$( printf '%o' $(( 0777 & ~$l_mask)) )"
   l_users="$(awk -v pat="$l_valid_shells" -F: '$(NF) ~ pat { print $1 " " $(NF-1) }' /etc/passwd | wc -l)"
   [ "$l_users" -gt 10000 ] && printf '%s\n' "" "  ** INFO **" \
   "  $l_users Local interactive users found on the system" "  This may be a long running check" "  **********"
   while IFS=" " read -r l_user l_home; do
      if [ -d "$l_home" ]; then
         while IFS=: read -r l_own l_mode; do
            [ "$l_user" != "$l_own" ] && a_owner2+=("  - User: \"$l_user\" Home \"$l_home\" is owned by: \"$l_own\"")
            [ $(( $l_mode & $l_mask )) -gt 0 ] && a_mode2+=("  - User: \"$l_user\" Home \"$l_home\" is mode: \"$l_mode\"" \
            "    should be mode: \"$l_max\" or more restrictive")
         done <<< "$(stat -Lc '%U:%#a' "$l_home")"
      else
         a_exists2+=("  - User: \"$l_user\" Home Directory: \"$l_home\" Doesn't exist")
      fi
   done <<< "$(awk -v pat="$l_valid_shells" -F: '$(NF) ~ pat { print $1 " " $(NF-1) }' /etc/passwd)"
   [ "${#a_exists2[@]}" -gt 0 ] && a_output2+=("${a_exists2[@]}") || \
   a_output+=("  - All interactive users home directories exist")
   [ "${#a_mode2[@]}" -gt 0 ] && a_output2+=("${a_mode2[@]}") || \
   a_output+=("  - All interactive users home directories are mode \"$l_max\" or more restrictive")
   [ "${#a_owner2[@]}" -gt 0 ] && a_output2+=("${a_owner2[@]}") || \
   a_output+=("  - All interactive users own their home directory")
   if [ "${#a_output2[@]}" -le 0 ]; then
      printf '%s\n' "" "- Audit Result:" "  ** PASS **" "${a_output[@]}"
   else
      printf '%s\n' "" "- Audit Result:" "  ** FAIL **" " - Reason(s) for audit failure:" "${a_output2[@]}"
      [ "${#a_output[@]}" -gt 0 ] && printf '%s\n' "- Correctly set:" "${a_output[@]}"
   fi
}