#!/usr/bin/env bash

source ./pre_run.sh

if [ "$WEB_APP" = true ] || [ "$WEB_APP" = "true" ] ; then
  printf "\nStarting web app\n\n"
  python3 aideas/web.py  # --agents translation --browser-visible true
else
  printf "\nStarting app\n\n"
  python3 aideas/main.py  # --agents translation --browser-visible true
fi