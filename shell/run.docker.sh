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

docker-compose build aideas

APP_USER_HOME="/root"
APP_USER_ID=0

# We don't want directories like OUTPUT_DIR, which our container
# accesses to change (at least within the container), so we use a
# fixed value for such directories. The value is fixed even though
# the host directory they are bound to changes.
docker-compose run -u "$APP_USER_ID" -p "${APP_PORT}:${APP_PORT}" \
  -v /etc/localtime:/etc/localtime \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -v "${OUTPUT_DIR}:${APP_USER_HOME}/.aideas/output" \
  -v "${CONTENT_DIR}:${APP_USER_HOME}/.aideas/content" \
  -v "${CHROME_PROFILE_DIR}:${APP_USER_HOME}/.config/google-chrome" \
  -e OUTPUT_DIR="${APP_USER_HOME}/.aideas/output" \
  -e CONTENT_DIR="${APP_USER_HOME}/.aideas/content" \
  -e CHROME_PROFILE_DIR="${APP_USER_HOME}/.config/google-chrome" \
  aideas