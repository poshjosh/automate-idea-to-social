#!/bin/bash

log() {

  local parts=($1)
  local first="${parts[0]}"
  local log=true

  if [ ! -z "${LOG_TAGS+x}" ] && [ "$LOG_TAGS" != '' ]; then
    if [[ "$LOG_TAGS" != *"$first"* ]]; then
      log=false
    fi
  fi

  if [ "$log" = true ]; then
    echo "$(date '+%T') ${1}"
  fi
}

error () {
    log "ERROR ${1}"
}

warn () {
    log "WARNING ${1}"
}

info () {
    log "INFO ${1}"
}

debug () {
    log "DEBUG ${1}"
}

trace() {
    log "TRACE ${1}"
}

printloc() {

    local msg="Current directory: $(pwd)"

    if [ "$VERBOSE" = true ]; then
        trace "$msg" && ls -a
    else [ "$PROFILE" != 'prod' ]
        debug "$msg";
    fi
}

string_length() {
    local slen=$(echo -n $1 | wc -m)
    debug "Length: $slen of text: $1"
    echo $slen
}

to_reference_fmt() {
    echo "\${${1}}"
}

# Arg 0 - content to write e.g "Hello World"
# Arg 1 - directory name   e.g /jumping/jack/flash
# Arg 2 - file name        e.g /test.txt
write_to_file() {
    if [ ! -d "$2" ]; then
        mkdir -p $2
    fi
    echo "$1" > $3
}

# Arg 1 - text to extract date from
# Arg 2 - seperator for date (e.g -) will be applied thus: 2014-10-13 etc
extract_date_having_separator() {
    # dddd-dd-dd
    local regex1=$(echo "\b[[:digit:]]{4}$2[[:digit:]]{2}$2[[:digit:]]{2}\b")
    local found=$(echo $1 | grep -Eo $regex1)
    if [ -z "$found" ]; then
        # dd-dd-dddd
        local regex2=$(echo "\b[[:digit:]]{2}$2[[:digit:]]{2}$2[[:digit:]]{4}\b")
        found=$(echo $1 | grep -Eo $regex2)
    fi
    echo $found
}

# Arg 1 - The text to extract date from
# Supported separators /, -, \, _ e.g for / is 2014/10/23
extract_date() {
    local mfound=$(extract_date_having_separator $1 '/')
    if [ -z "$mfound" ]; then
        mfound=$(extract_date_having_separator $1 '-')
        if [ -z "$mfound" ]; then
            mfound=$(extract_date_having_separator $1 '\')
            if [ -z "$mfound" ]; then
                mfound=$(extract_date_having_separator $1 '_')
            fi
        fi
    fi
    echo $mfound
}

move_dir_content_to_parent() {
    debug "Moving content of current directory up one level"
    info "For next command, IGNORE THIS WARNING -> mv: can't rename '.': Resource busy"
    printloc
    find . -maxdepth 1 -exec mv {} .. \;
    (cd .. && printloc)
}

emplace_zip_file_content_and_delete_zip_file() {

    local files=$(find "${1}" -maxdepth 1)
    local file_count=${#files[@]}
    debug "Found $file_count files in current directory"

    if [ $file_count == 1 ]; then
        local dir=''
        for item in ${files[*]}
        do
            local fname=$(echo ${item})
            trace "$fname"

            if [ "$fname" == '.' ] || [ "$fname" == '..' ]; then
                debug "Skipping file: $fname"
            elif [ "$fname" == "$1" ]; then
                debug "Skipping $fname"
            elif [[ ${fname} == *.zip ]]; then
                debug "Removing zip file: $fname"
                rm -f "${fname}"
            elif [ -d "$fname" ]; then
                debug "Found directory: $fname"
                dir=$fname
            else
                warn ": What would you have me do with this file? $fname"
            fi
        done

        if [ "$dir" == '' ]; then
            error ": Directory unpacked from .zip file not found"
        else
            debug "Found directory: $dir"
            (cd ${dir} && move_dir_content_to_parent)
            debug "Deleting ${dir}"
            rm -Rf ${dir}
        fi
    fi

    (cd ${1} && (debug "Removing zip files in: $1" & rm -Rf *.zip))
}

# arg 1 - source to download from
# arg 2 - target to download to
download_and_unzip_into_dir() {

    local msg="Downloading from: ${1}"

    (cd ${2} && curl -LO $1) && debug "SUCCESS: $msg" || error ": $msg"

    (cd ${2} && printloc)

    if [[ ${1} == *.zip ]]; then

        msg="Unzipping downloaded content into: ${2}"
        debug "${msg}"

        (cd ${2} && unzip -q *.zip) && debug "SUCCESS: $msg" || error ": $msg"
    fi

    emplace_zip_file_content_and_delete_zip_file ${2}

    (cd ${2} && printloc)
}

# arg 1 - source to clone from
# arg 2 - target to clone to
git_clone_into_dir() {

    local msg="Performing git clone from ${1} into: ${2}"

    debug "${msg}"

    git clone ${1} ${2} && debug "SUCCESS: $msg" || error ": $msg"

    (cd ${2} && rm -Rf '.git')

    (cd ${2} && printloc)
}

# arg 1 - source to copy from
# arg 2 - target to copy to
copy_dir_contents() {

    local msg="Copying directory contents from ${1} to ${2}"
    debug "${msg}"

    (cd ${1} && printloc)

    cp -R "${1}/." ${2} && debug "SUCCESS: $msg" || error ": $msg"

    (cd ${2} && printloc)
}

# arg 1 - source to import from (Will be created if it doesn't exist)
# arg 2 - target to import to
import() {

   if [ ! -d "${2}" ]; then mkdir -p "${2}"; fi

    if [[ ${1} == http* ]]; then

        if [[ ${1} == *.git ]]; then

            git_clone_into_dir ${1} ${2}

        else

            download_and_unzip_into_dir ${1} ${2}
        fi
    else

        copy_dir_contents ${1} ${2}
    fi
}
