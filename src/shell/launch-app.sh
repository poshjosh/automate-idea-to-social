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

printf "\nExporting environment\n"

set -a
source ../../.env
set +a

cd ../python/main ||
(echo "Could not change from script dir to working dir: ../src/python/main" && exit 1)

printf "\nWorking from: %s\n" "$(pwd)"

if [ "${SKIP_RUN}" = "true" ] || [ "$SKIP_RUN" = true ]; then
  printf "\nSkipping run\n"
  exit 0
else
  printf "\nLaunching app\n"
  "$PYTHON" ./app/main.py
fi