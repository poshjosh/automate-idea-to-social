#!/usr/bin/env bash

set -euo pipefail

#@echo off

cd .. || exit 1

printf "\nCreating virtual environment\n"
python3 -m venv .venv

printf "\nActivating virtual environment\n"
source .venv/bin/activate

cd "src/aideas" || exit 1

printf "\nSaving dependencies to requirements.txt\n"
pip-compile requirements.in > requirements.txt

printf "\nInstalling dependencies\n"
python3 -m pip install -r requirements.txt
