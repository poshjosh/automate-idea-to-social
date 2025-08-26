#!/usr/bin/env bash

set -euo pipefail

cd .. || exit 1 # we start from project root
printf "\nWorking from: %s\n" "$(pwd)"

set -a
source .env
set +a

BUILD=${BUILD:-false}
BUILD_CONTEXT=${BUILD_CONTEXT:-"src/aideas"} # relative to project root
IMAGE=${IMAGE:-"poshjosh/aideas:${APP_VERSION:-latest}"}
SKIP_RUN=${SKIP_RUN:-false}
VERBOSE=${VERBOSE:-false}

[ "${VERBOSE}" = "true" ] || [ "$VERBOSE" = true ] && set -o xtrace

chmod +x src/aideas/docker-entrypoint.sh

docker system prune -f

# Build docker image if build=true, or the image doesn't exist

docker images | grep "${IMAGE}" && res="y" || res="n"

if [ "$BUILD" = true ] || [ "$BUILD" = "true" ] || [ "${res}" = "n" ]; then
    printf "\nBuilding image: %s\n" "${IMAGE}"
    docker build -t "${IMAGE}" --progress=plain "${BUILD_CONTEXT}"
fi

#           input=IMAGE: poshjosh/abc:latest
# output=CONTAINER_NAME: poshjosh-abc-latest
CONTAINER_NAME=$(echo "$IMAGE" | tr / - | tr : -)
printf "\nContainer name: %s\n" "${CONTAINER_NAME}"

# Stop docker container if it is running
docker ps -a | grep "$CONTAINER_NAME" && res="y" || res="n"
if [ "${res}" == "y" ]; then
    printf "\nStopping container: %s" "$CONTAINER_NAME"
    # runs the command for 30s, and if it is not terminated, it will kill it after 10s.
    timeout --kill-after=10 30 docker container stop "$CONTAINER_NAME"
fi

if [ "${SKIP_RUN}" = "true" ] || [ "$SKIP_RUN" = true ]; then
    printf "\nSkipping image run, since SKIP_RUN is true"
else
    printf "\nRunning image: %s" "${IMAGE}"
    docker run -u 0 -it --name "$CONTAINER_NAME" \
        -p "${APP_PORT:-5000}:${APP_PORT:-5000}" \
        -v /etc/localtime:/etc/localtime \
        -v /var/run/docker.sock:/var/run/docker.sock \
        -v "${HOME}/.aideas:/root/.aideas" \
        --env-file .env \
        -e "APP_PROFILES=docker,${APP_PROFILES:-default}" \
        --shm-size=2g \
        "${IMAGE}"
fi

printf "\nPruning docker system\n"
docker system prune -f

printf "\nSUCCESS\n"