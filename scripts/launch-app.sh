#!/usr/bin/env bash

#set -euo pipefail

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

function changeToScriptDir() {
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

printf "\nExporting environment\n"

cd ..

set -a
source .env
set +a

cd ./src/python/main || (echo "Could not change from script dir to working dir: ./src/python/main" && exit 1)

printf "\nWorking from: %s\n" "$(pwd)"

if [ "${SKIP_RUN}" = "true" ] || [ "$SKIP_RUN" = true ]; then
  printf "\nSkipping run\n"
  exit 0
else
  printf "\nLaunching app\n"
  "$PYTHON" ./main.py
fi