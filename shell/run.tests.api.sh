#!/usr/bin/env bash

######################### WARNING ! ########################
# The service must be running before executing this script.
# First run the script shell/run.sh to start the service.
############################################################

cd .. || exit 1

printf "\nExporting environment\n"

set -a
source .env
set +a

APP_PORT="${APP_PORT:-5000}"

# On macos, we need to install coreutils to get gnu date
# This next line is done to use gnu date as default.
# See https://apple.stackexchange.com/questions/135742/time-in-milliseconds-since-epoch-in-the-terminal
export PATH="/usr/local/opt/coreutils/libexec/gnubin:$PATH"
function log() {
  printf "%s %s\n" "$(date +'%T.%3N')" "$1"
}

# GET /api/agents
URL="http://localhost:${APP_PORT}/api/agents?tag=test"
log ""
log " GET ${URL}"
output=$(curl -s -H 'Content-Type: application/json' -X GET "${URL}")
log "Expected: {
  \"agents\": [
  ...
  ],
  \"tag\": \"test\"
}
"
log "  Actual: ${output}"

# GET /api/agents/test-agent
URL="http://localhost:${APP_PORT}/api/agents/test-agent"
log ""
log " GET ${URL}"
output=$(curl -s -H 'Content-Type: application/json' -X GET "${URL}")
log "Expected: agent configuration file"
log "  Actual: ${output}"

# POST /api/tasks?action=start
URL="http://localhost:${APP_PORT}/api/tasks?action=start"
data="{\"tag\":\"test\", \"agents\":[\"test-agent\", \"test-log\"] }"
log ""
log "POST ${URL} ${data}"
output=$(curl -s -H 'Content-Type: application/json' -X POST -d "$data" "${URL}")
log "Expected: {
  \"id\": \"********************************\"
}
"
log "  Actual: ${output}"

# GET /api/tasks
URL="http://localhost:${APP_PORT}/api/tasks"
log ""
log " GET ${URL}"
output=$(curl -s -H 'Content-Type: application/json' -X GET "${URL}")
log "Expected: {
 \"info\": null,
 \"tasks\": [
   {
     \"agents\": [
       \"test-agent\",
       \"test-log\"
     ],
     \"id\": \"********************************\",
     \"links\": {
       \"stop\": \"/api/tasks/********************************?action=stop\",
       \"view\": \"/api/tasks/********************************2\"
     },
     \"progress\": {
       \"test-agent\": \"PENDING >> LOADING >> RUNNING >> SUCCESS\",
       \"test-log\": \"PENDING >> LOADING >> RUNNING >> SUCCESS\"
     },
     \"status\": \"SUCCESS\"
   }
 ]
}"
log "  Actual: ${output}"

# /api/tasks/<task_id>



