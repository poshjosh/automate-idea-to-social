#!/usr/bin/env bash

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
data='{"tag":"post", "agents":["blog"], "share-cover-image": true,
"language-codes": ["ar","bn","de","en","es","fr","hi","it","ja","ko","ru","tr","uk","zh","zh-TW"],
"image-file-landscape": "/Users/chinomso/Desktop/live-above-3D/aideas-docker-mount/input/cover.jpg",
"text-file": "/Users/chinomso/Desktop/live-above-3D/aideas-docker-mount/input/If Jesus is God, who did He pray to.txt"}'
log ""
log "POST ${URL} ${data}"
output=$(curl -s -H 'Content-Type: application/json' -X POST -d "$data" -w "%{http_code}" "${URL}")
log "Output: ${output}"