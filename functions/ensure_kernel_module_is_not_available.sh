#!/usr/bin/env bash

{
   l_mod_name="$1" 
   l_mod_type="${2:-fs}"
   while IFS= read -r l_mod_path; do
      if [ -d "$l_mod_path/${l_mod_name/-/\/}" ] && [ -n "$(ls -A "$l_mod_path/${l_mod_name/-/\/}" 2>/dev/null)" ]; then
         printf '%s\n' "$l_mod_name exists in $l_mod_path"
      fi
   done < <(readlink -f /usr/lib/modules/**/kernel/$l_mod_type 2>/dev/null || readlink -f /lib/modules/**/kernel/$l_mod_type 2>/dev/null)
}