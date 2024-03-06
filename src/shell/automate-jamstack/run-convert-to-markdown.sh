#!/usr/bin/env bash

set -euo pipefail

printf "\nWorking from: %s" "$PWD"

source /Users/chinomso/dev_chinomso/automate-jamstack/scripts/convert-to-markdown.sh \
    -d '/Users/chinomso/dev_chinomso/automate-idea-to-social/src/python/main/resources/agent/pictory' \
    -e docx
