#!/usr/bin/env bash

ENV_FILE="${ENV_FILE:-.env}"
WORKING_DIR="src"

printf "\nEnvironment file: %s\n" "$ENV_FILE"

cd .. && source .venv/bin/activate || exit 1

printf "\nExporting environment\n"

set -a
# shellcheck source=.env
source "$ENV_FILE"
set +a

export PYTHONUNBUFFERED=1

cd "$WORKING_DIR" || (printf "\nCould not change to working dir: %s\n" "$WORKING_DIR" && exit 1)

printf "\nWorking from: %s\n" "$(pwd)"
