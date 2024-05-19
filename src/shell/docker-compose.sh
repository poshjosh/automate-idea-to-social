#!/usr/bin/env bash

#set -euo pipefail

#@echo off

cd ../.. || exit 1
docker-compose -p automate-idea-to-social up -d