#!/usr/bin/env bash

set -o errexit
set -o nounset
set -o pipefail
[[ -n ${DEBUG:-} ]] && set -o xtrace

#@echo off

#https://docs.python.org/3/library/unittest.html
#https://stackoverflow.com/questions/1896918/running-unittest-with-typical-test-directory-structure/24266885#24266885
# /Library/Frameworks/Python.framework/Versions/3.9/bin/python3
#python3 -m unittest discover -s . -p '/**/*_test.py'
#sudo find . -name '*_test.py' -exec python3 '-m unittest {}' \;

LINE="----------------------------------------------------------------------"
#exit|continue
ON_ERROR="exit"

run_unit_test() {
    local filepath="$1"
#    printf 'Test file: %s\n' "$filepath"
    path_without_ext=${filepath::${#filepath}-3}
    module_name=$(echo "$path_without_ext" | sed -r 's/[/]+/./g')
#    printf 'Module name: %s\n' "$module_name"
    module_name="${module_name:1}"
    module_name="${module_name:1}"
    printf '\n%s\nRunning unit tests in: %s\n%s\n' "$LINE" "$module_name" "$LINE"
    python3 -m unittest "$module_name"
}

run_tests_in_dir () {
    local total=0
    local passed=0
    # By setting the dotglob and nullglob shell options in bash, we are
    # able  to find hidden pathnames and will not have to test specially
    # for possibly empty directories.
    shopt -s nullglob dotglob
    for filepath in "$1"/*; do
        if [ -d "$filepath" ]; then
            run_tests_in_dir "$filepath"
        else
            case "$filepath" in *_test.py)
                total=$((total + 1))
                run_unit_test "$filepath" && passed=$((passed + 1))
            esac
        fi
    done

    local failed=$((total - passed))

    if [ "$total" -gt 0 ]; then
        printf '\n%s\nTotal: %d, Failed: %d, Passed: %d\n%s\n' "$LINE" "$total" "$failed" "$passed" "$LINE"
    fi

    if [ "$failed" -gt 0 ]; then
        if [ "${ON_ERROR}" = "exit" ]; then
            printf '\n%s\n!!! THERE WERE FAILED TESTS !!!\n%s\n' "$LINE" "$LINE"
            exit "$failed"
        fi
    fi
}

cd "/Users/chinomso/dev_chinomso/automate-idea-to-social/src" || exit 1

run_tests_in_dir .

printf '\n%s\n!!! COMPLETED ALL TESTS SUCCESSFULLY !!!\n%s\n' "$LINE" "$LINE"
