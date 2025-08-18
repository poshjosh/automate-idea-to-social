#!/usr/bin/env bash
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
            # Window size should match that in browser.config.yaml and other browser-xxx.yaml files.
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

printf "\nGranting permission 775 to: %s\n" "${OUTPUT_DIR}" && chmod 775 "${OUTPUT_DIR}" \
    && printf "\nGranting permission 775 to: %s\n" "${CONTENT_DIR}" && chmod 775 "${CONTENT_DIR}"

#printf "\nRunning: %s\n" "$@"
#exec "$@"

#echo $(whoami) && echo "$(pwd)" && ls -aol && cd aideas && echo "$(pwd)" && ls -aol && cd ..

cd aideas || exit 1 # The app expect to work from within the aideas directory.

if [ "$WEB_APP" = true ] || [ "$WEB_APP" = "true" ] ; then
  python3 web.py "$RUN_ARGS"
else
  python3 main.py "$RUN_ARGS"
fi
