#!/usr/bin/env bash

set -euo pipefail

cd ..

printf "\nActivating virtual environment\n"
source .venv/bin/activate

# Make main modules accessible to test modules
python3 -m pip install -e .
