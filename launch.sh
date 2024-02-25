#!/usr/bin/env bash

set -o errexit
set -o nounset
set -o pipefail
[[ -n ${DEBUG:-} ]] && set -o xtrace

PROJECT_DIR="/Users/chinomso/dev_chinomso/automate-idea-to-social"
APP_DIR="${PROJECT_DIR}/src/python/main"

cd /usr/local/bin

python3 "${APP_DIR}/main.py"