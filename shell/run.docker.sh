#!/usr/bin/env bash

cd .. || exit 1

set -a
source .env # Currently we only use OUTPUT_DIR from the .env file, directly here.
set +a

if [ ! -d "${OUTPUT_DIR}" ]; then
    printf "\nCreating output directory: %s\n" "${OUTPUT_DIR}"
    mkdir -p "${OUTPUT_DIR}" || (printf "\nFailed create output directory: %s\n" "${OUTPUT_DIR}" && exit 1)
fi

chmod +x src/aideas/docker-entrypoint.sh

docker system prune -f

# To log output of the build process.
export BUILDKIT_PROGRESS=plain

docker-compose -p automate-idea-to-social up -d