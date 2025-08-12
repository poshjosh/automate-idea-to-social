#!/usr/bin/env bash

source ./pre_run.sh

if [ "$WEB_APP" = true ] || [ "$WEB_APP" = "true" ] ; then
  printf "\nStarting web app\n\n"
  python3 aideas/web.py "$RUN_ARGS"
else
  printf "\nStarting app\n\n"
  python3 aideas/main.py "$RUN_ARGS"
fi