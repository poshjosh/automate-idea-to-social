#!/usr/bin/env bash

set -o errexit
set -o nounset
set -o pipefail

#@echo off

# Usage: ./<script-file>.sh -b <BUILD build image even if it exists> -d <DIR> -e <ENV_FILE> \
# -i <IMAGE docker image> -p <PORT> -s <true|false, skip run> -v <true|false, verbose>

BUILD=false
DIR='.'
PORT=8000
SKIP_RUN=false
VERBOSE=false

while getopts b:d:e:i:p:s:v: flag
do
    case "${flag}" in
        b) BUILD=${OPTARG};;
        d) DIR=${OPTARG};;
        e) ENV_FILE=${OPTARG};;
        i) IMAGE=${OPTARG};;
        p) PORT=${OPTARG};;
        s) SKIP_RUN=${OPTARG};;
        v) VERBOSE=${OPTARG};;
        *) exit 1;;
    esac
done

[ "${VERBOSE}" = "true" ] || [ "$VERBOSE" = true ] && set -o xtrace

# By getting the script's dir, we can run the script from any where. 
function getScriptDir() {
  local script_path="${BASH_SOURCE[0]}"
  local script_dir;
  while [ -L "${script_path}" ]; do
    script_dir="$(cd -P "$(dirname "${script_path}")" >/dev/null 2>&1 && pwd)"
    script_path="$(readlink "${script_path}")"
    [[ ${script_path} != /* ]] && script_path="${script_dir}/${script_path}"
  done
  script_path="$(readlink -f "${script_path}")"
  cd -P "$(dirname -- "${script_path}")" >/dev/null 2>&1 && pwd
}

script_dir=$(getScriptDir)

cd "$script_dir" || (printf "\nCould not change to script directory: %s" "$script_dir"
                     exit 1)

printf "\nChanging to app directory: %s" "${DIR}"

cd "$DIR" || (printf "\nCould not change to app directory: %s" "$DIR"
              exit 1)

# Build docker image if it doesn't exist

docker images | grep "${IMAGE}" && res="y" || res="n"

if [ "$BUILD" = true ] || [ "$BUILD" = "true" ] || [ "${res}" = "n" ]; then
    printf "\nBuilding image: %s" "${IMAGE}"
    docker build -t "${IMAGE}" .
fi

#           input=IMAGE: poshjosh/liveabove3d-latest
# output=container_name: poshjosh-liveabove3d-latest
container_name=$(echo "$IMAGE" | tr / -)

# Stop docker container if it is running
docker ps -a | grep "$container_name" && res="y" || res="n"
if [ "${res}" == "y" ]; then
    printf "\nStopping container: %s" "$container_name"
    # runs the command for 30s, and if it is not terminated, it will kill it after 10s.
    timeout --kill-after=10 30 docker container stop "$container_name"
fi

printf "\nUsing environment file: %s" "${ENV_FILE}"

printf "\nWill mount: %s/app and use port %s" "${DIR}" "${PORT}"

if [ "${SKIP_RUN}" = "true" ] || [ "$SKIP_RUN" = true ]; then
    printf "\nSkipping app run, since SKIP_RUN is true"
else
    printf "\nRunning image: %s" "${IMAGE}"
    docker run --name "$container_name" --rm -v "${DIR}/app":/app \
        --env-file "${ENV_FILE}" \
        -u 0 -p "${PORT}:${PORT}" -e "APP_PORT=$PORT" "${IMAGE}"
fi

printf "\nPruning docker system\n"
docker system prune -f

printf "\nSUCCESS\n"
