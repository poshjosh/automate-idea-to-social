#!/usr/bin/env bash

source ./pre_run.sh

printf "\nStarting tests\n\n"

python3 -m unittest discover -s test/app -p "*_test.py"
#python3 -m unittest discover -s test/app -p "config_loader_test.py"
#python3 -m unittest discover -s test/app/action -p "*element_action_handler_test.py"
#python3 -m unittest discover -s test/app/action -p "*variable_parser_test.py"
#python3 -m unittest discover -s test/app/agent -p "*blog_agent_test.py"
#python3 -m unittest discover -s test/app/result -p "*result_set_test.py"
