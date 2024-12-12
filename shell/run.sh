#!/usr/bin/env bash

WORKING_DIR="src"

cd .. && source .venv/bin/activate || exit 1

printf "\nExporting environment\n"

set -a
source .env
set +a

export PYTHONUNBUFFERED=1

cd "$WORKING_DIR" || (printf "\nCould not change to working dir: %s\n" "$WORKING_DIR" && exit 1)

printf "\nWorking from: %s\n" "$(pwd)"

if [ "$WEB_APP" = true ] || [ "$WEB_APP" = "true" ] ; then
  printf "\nStarting web app\n\n"
  python3 aideas/web.py  # --agents translation
else
  printf "\nStarting app\n\n"
  python3 aideas/main.py  # --agents translation
fi