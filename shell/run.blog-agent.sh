#!/usr/bin/env bash

IMAGE_FILE=${IMAGE_FILE:-"/root/.aideas/content/cover.jpg"}
TEXT_FILE=${TEXT_FILE:-"/root/.aideas/content/content.txt"}

cd .. || exit 1

set -a
source .env # Currently we only use APP_PORT from the .env file, directly here.
set +a

# On macos, we need to install coreutils to get gnu date
# This next line is done to use gnu date as default.
# See https://apple.stackexchange.com/questions/135742/time-in-milliseconds-since-epoch-in-the-terminal
export PATH="/usr/local/opt/coreutils/libexec/gnubin:$PATH"
function log() {
  printf "%s %s\n" "$(date +'%T.%3N')" "$1"
}

URL="http://localhost:${APP_PORT}/api/tasks"
data="{\"agents\":[\"blog\"], \"share-cover-image\": true,
\"image-file-landscape\": \"$IMAGE_FILE\",
\"text-file\": \"$TEXT_FILE\"}"
log ""
log "POST ${URL} ${data}"
output=$(curl -s -H 'Content-Type: application/json' -X POST -d "$data" -w "%{http_code}" "${URL}")
log "Output: ${output}"