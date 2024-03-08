#!/usr/bin/env bash

set -o errexit
set -o nounset
set -o pipefail
[[ -n ${DEBUG:-} ]] && set -o xtrace

#@echo off

printf "\nEnter site name without http://, e.g my-site.com\n"

read -r SITE_NAME

DIR="${HOME}/dev_chinomso/automate-jamstack"
IMAGE="poshjosh/automate-jamstack"

source ./docker-run-app.sh -d "${DIR}" -e "${DIR}/app/sites/${SITE_NAME}.env" -i "$IMAGE"

read -n 1 -s -r -p "Press any key to continue"
