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
ENDPOINT="http://localhost:${APP_PORT}/api"

# On macos, we need to install coreutils to get gnu date
# This next line is done to use gnu date as default.
# See https://apple.stackexchange.com/questions/135742/time-in-milliseconds-since-epoch-in-the-terminal
export PATH="/usr/local/opt/coreutils/libexec/gnubin:$PATH"
function log() {
  printf "%s %s\n" "$(date +'%T.%3N')" "$1"
}

# GET /api/agents
URL="${ENDPOINT}/agents"
log ""
log " GET ${URL}"
output=$(curl -s -H 'Content-Type: application/json' -X GET -w "%{http_code}" "${URL}")
if [[ "$output" == *200 ]]; then
  log "SUCCESS"
else
  log "FAILURE"
  log 'Expected: {
    "agents": [
    ...
    ],
    "tag": null
  }
  '
  log "  Actual: ${output}"
fi

# GET /api/agents?tag=test
URL="${ENDPOINT}/agents?tag=test"
log ""
log " GET ${URL}"
output=$(curl -s -H 'Content-Type: application/json' -X GET -w "%{http_code}" "${URL}")
if [[ "$output" == *200 ]]; then
  log "SUCCESS"
else
  log "FAILURE"
  log 'Expected: {
    "agents": [
    ...
    ],
    "tag": "test"
  }
  '
  log "  Actual: ${output}"
fi

# GET /api/agents/test-agent
URL="${ENDPOINT}/agents/test-agent"
log ""
log " GET ${URL}"
output=$(curl -s -H 'Content-Type: application/json' -X GET -w "%{http_code}" "${URL}")
if [[ "$output" == *200 ]]; then
  log "SUCCESS"
else
  log "FAILURE"
  log "Expected: agent configuration file"
  log "  Actual: ${output}"
fi

# POST /api/tasks
URL="${ENDPOINT}/tasks"
data='{"agents":["test-agent", "test-log"] }'
log ""
log "POST ${URL} ${data}"
output=$(curl -s -H 'Content-Type: application/json' -X POST -d "$data" -w "%{http_code}" "${URL}")
if [[ "$output" == *201 ]]; then
  log "SUCCESS"
else
  log "FAILURE"
  log 'Expected: {
    "id": "********************************"
  }
  '
  log "  Actual: ${output}"
fi

# GET /api/tasks
URL="${ENDPOINT}/tasks"
log ""
log " GET ${URL}"
output=$(curl -s -H 'Content-Type: application/json' -X GET -w "%{http_code}" "${URL}")
if [[ "$output" == *200 ]]; then
  log "SUCCESS"
else
  log "FAILURE"
  log 'Expected: {
   "info": null,
   "tasks": [
     {
       "agents": [
         "test-agent",
         "test-log"
       ],
       "id": "********************************",
       "links": {
         "stop": "/api/tasks/********************************?action=stop",
         "view": "/api/tasks/********************************2"
       },
       "progress": {
         "test-agent": "PENDING >> LOADING >> RUNNING >> SUCCESS",
         "test-log": "PENDING >> LOADING >> RUNNING >> SUCCESS"
       },
       "status": "SUCCESS"
     }
   ]
  }'
  log "  Actual: ${output}"
fi

# GET /api/tasks/<task_id>



