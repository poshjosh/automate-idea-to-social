#!/usr/bin/env bash

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT_DIR"

cd ..

printf "\nActivating virtual environment\n"
source .venv/bin/activate

printf "\nInstalling module for local development: %s\n" "$(pwd)"
python3 -m pip install -r src/aideas/requirements.txt
# Make main modules accessible to test modules
python3 -m pip install -e .
