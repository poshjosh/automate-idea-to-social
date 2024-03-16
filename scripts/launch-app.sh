#!/usr/bin/env bash

set -euo pipefail

#@echo off

# Usage: ./<script-file>.sh -p <PYTHON> -s <true|false, skip run> -v <true|false, verbose>

#PYTHON="/usr/local/bin/python3.9"
PYTHON="python3"
SKIP_RUN=false
VERBOSE=false

while getopts p:s:v: flag
do
    case "${flag}" in
        p) PYTHON=${OPTARG};;
        s) SKIP_RUN=${OPTARG};;
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

SCRIPT_DIR=$(getScriptDir)

cd "$SCRIPT_DIR" || (echo "Could not change to script directory: $SCRIPT_DIR" && exit 1)

printf "\nExporting environment\n"

function get_env() {
  # /^#/d removes comments (strings that start with #)
  # /^\s*$/d removes empty strings, including whitespace
  # "s/'/'\\\''/g" replaces every single quote with '\'', which is a trick sequence in bash to produce a quote :)
  # "s/=\(.*\)/='\1'/g" converts every a=b into a='b'
  cat ../.env | sed -e '/^#/d;/^\s*$/d' -e "s/'/'\\\''/g" # -e "s/=\(.*\)/='\1'/g"
}

if [ "${VERBOSE}" = "true" ] || [ "$VERBOSE" = true ]; then
    printf "\nEnvironment:\n"
    cat <(get_env)
fi

set -a
#source ../.env
source <(get_env)
set +a

# TODO - The check below reveals that our export of env above isn't working
#  video.cover.image and other video related environments are not printed.
env | grep USER
env | grep video

cd ../src/python/main || (echo "Could not change from script dir to working dir: ../src/python/main" && exit 1)

printf "\nWorking from: %s\n" "$(pwd)"

if [ "${SKIP_RUN}" = "true" ] || [ "$SKIP_RUN" = true ]; then
  printf "\nSkipping run\n"
  exit 0
else
  printf "\nLaunching app\n"
  "$PYTHON" ./main.py
fi