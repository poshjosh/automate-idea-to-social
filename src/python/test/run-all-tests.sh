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

run_unit_test() {
    local line="----------------------------------------------------------------------"
    local filepath="$1"
    printf '%s\n' "$filepath"
    path_without_ext=${filepath::${#filepath}-3}
    module_name=$(echo "$path_without_ext" | sed -r 's/[/]+/./g')
    printf '%s\n' "$module_name"
    module_name="${module_name:1}"
    module_name="${module_name:1}"
    printf '\n%s\nRunning unit tests in: %s\n%s\n' "$line" "$module_name" "$line"
    python3 -m unittest "$module_name"
}

walk_dir () {
    # By setting the dotglob and nullglob shell options in bash, we are
    # able  to find hidden pathnames and will not have to test specially
    # for possibly empty directories.
    shopt -s nullglob dotglob
    #line="----------------------------------------------------------------------"
    line="x x x x x x x x x x x x x x x x x x x x x x x x x x x x x x x x x x x x"
    for filepath in "$1"/*; do
        if [ -d "$filepath" ]; then
            walk_dir "$filepath"
        else
            case "$filepath" in *_test.py)
                run_unit_test "$filepath"
            esac
        fi
    done
}

cd '/Users/chinomso/dev_chinomso/automate-idea-to-social/src' || exit 1
walk_dir .