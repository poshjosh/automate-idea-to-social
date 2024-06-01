#!/usr/bin/env bash

#@echo off

cd .. || exit 1

# Add `BUILDKIT_PROGRESS=plain` before the docker-compose command
# to log output of the build process.
docker-compose -p automate-idea-to-social up -d