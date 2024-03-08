#!/usr/bin/env bash

set -euo pipefail

#@echo off

# Usage: ./<script-file>.sh -d <DIR> -e <EXT> -s <true|false, skip run> -v <true|false, verbose>

DIR='.'
EXT='docx'
SKIP_CONVERT=false
VERBOSE=false

while getopts d:e:s:v: flag
do
    case "${flag}" in
        d) DIR=${OPTARG};;
        e) EXT=${OPTARG};;
        s) SKIP_CONVERT=${OPTARG};;
        v) VERBOSE=${OPTARG};;
        *) exit 1;;
    esac
done

[ "${VERBOSE}" = "true" ] || [ "$VERBOSE" = true ] && set -o xtrace

# By getting the script's dir, we can run the script from any where. 
function getScriptDir() {
  local script_path="${BASH_SOURCE[0]}"
  local script_dir;
  while [ -L "${script_path}" ]; do
    script_dir="$(cd -P "$(dirname "${script_path}")" >/dev/null 2>&1 && pwd)"
    script_path="$(readlink "${script_path}")"
    [[ ${script_path} != /* ]] && script_path="${script_dir}/${script_path}"
  done
  script_path="$(readlink -f "${script_path}")"
  cd -P "$(dirname -- "${script_path}")" >/dev/null 2>&1 && pwd
}

script_dir=$(getScriptDir)

cd "$script_dir" || (echo "Could not change to script directory: $script_dir" && exit 1)

dir="${DIR:-.}"

printf "\nWorking directory: %s\n" "$dir"

declare -i convert_count=0

unwanted_prefix="~$"

IFS=$'\n'; set -f
for f in $(find "$dir" -name "*.$EXT"); do
  printf "\nSource: %s" "$f"
  filename=$(basename "$f")
  if [[ "$filename" == "$unwanted_prefix"* ]]; then
    printf "\nSkipping due to unwanted prefix: %s\n" "$f"
    continue
  fi

  fdate=$(date -r "$f" "+%Y/%m/%d")
  fdir="blog/$fdate"
  cd "$dir" || exit 1
  mkdir -p "$fdir"
  new_dir="$dir/$fdir"
  new_file=$(echo "${f%.*}.md" | sed -e "s^${dir}^${new_dir}^1" -e "s/ /-/g")
  new_filename=$(basename "$new_file")
  new_file="$new_dir/$new_filename"

  printf "\nTarget: %s\n" "$new_file"
  if [ "${SKIP_CONVERT}" = "true" ] || [ "$SKIP_CONVERT" = true ]; then
    printf "\nSkipping because SKIP is true: %s\n" "$f"
  else
    if [[ "$EXT" == "txt" ]]; then
      cp "$f" "${new_file}"
    else
      pandoc --standalone --table-of-contents=true --from "$EXT" --to markdown_strict "$f" --output "$new_file"
    fi
  fi

  convert_count=$((convert_count+1))
done
unset IFS; set +f

printf "\nConverted %s files to markdown" "$convert_count"
printf "\nSUCCESS\n"