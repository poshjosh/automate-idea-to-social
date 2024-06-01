#!/usr/bin/env bash

###############################################################################
# Run this script so that the `aideas` package is available for test modules. #
###############################################################################

cd .. && source .venv/bin/activate || exit 1

python3 -m pip install --upgrade pip

python3 -m pip install -e .
