#!/usr/bin/env bash

# shellcheck disable=SC2034
ENV_FILE=".env.test"
source ./pre_run.sh

WORKING_DIR="src"

cd "$WORKING_DIR" || (printf "\nCould not change to working dir: %s\n" "$WORKING_DIR" && exit 1)

printf "\nWorking from: %s\n" "$(pwd)"

printf "\nStarting tests\n\n"

python3 -m unittest discover -s test/app -p "*test.py"

printf "\nStarting integration tests\n\n"

python3 -m unittest discover -s test/app -p "*it.py"

#python3 -m unittest discover -s test/app -p "config_loader_test.py"
#python3 -m unittest discover -s test/app/action -p "*element_action_handler_test.py"
#python3 -m unittest discover -s test/app/action -p "*variable_parser_test.py"
#python3 -m unittest discover -s test/app/agent -p "*blog_agent_test.py"
#python3 -m unittest discover -s test/app/result -p "*result_set_test.py"
