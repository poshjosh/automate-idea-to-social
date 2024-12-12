#!/bin/bash
# print debug information
#set -ex

function grantExecutePermissionToShellScriptsInDir() {
    IFS=$'\n'; set -f
    for f in $(find "$1" -name "*.sh"); do
      printf "\nGranting execute permission to: %s\n" "$f"
      chmod +x "$f"
    done
    unset IFS; set +f
}

function keepUpScreen() {
    printf "\nKeeping up screen\n"
    while true; do
        sleep 1
        if [ -z "$(pidof -x Xvfb)" ]; then
            # Window size should match that in app.config.yaml
            Xvfb "$DISPLAY" -screen "$DISPLAY" 1920x1080x16 &
        fi
    done
}

grantExecutePermissionToShellScriptsInDir "${OUTPUT_DIR}"

# Our python image uses a minimal debian, so we need to do
# the following for undetected chrome browser to work well.
# See https://github.com/ultrafunkamsterdam/undetected-chromedriver/issues/743
if [ "$SETUP_DISPLAY" = true ] || [ "$SETUP_DISPLAY" = "true" ] ; then
  export DISPLAY=:1
  rm -f /tmp/.X1-lock &>/dev/null
  keepUpScreen &
fi

#printf "\nRunning: %s\n" "$@"
#exec "$@"
if [ "$WEB_APP" = true ] || [ "$WEB_APP" = "true" ] ; then
  exec python web.py
else
  exec python main.py
fi
