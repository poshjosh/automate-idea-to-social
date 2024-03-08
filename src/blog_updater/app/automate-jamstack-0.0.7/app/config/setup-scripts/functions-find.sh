#!/bin/bash

source ${g_scripts_dir}/functions-util.sh

# arg 1 - target text
# arg 2 - to-replace
# arg 3 - replacement
#
find_and_replace_text_in_text() {

    return_value_find_and_replace_text_in_text=$1

    if [ -z ${3+x} ] || [ "${3}" == '' ]; then
        trace "Replacement not available for: ${2} of ${1}"
    else
        #@TODO ensure replacement took place by searching for the variable that
        # was replaced
        return_value_find_and_replace_text_in_text=$(echo $1 | sed -e "s^${2}^${3}^g")
        if [ $return_value_find_and_replace_text_in_text == $1 ]; then
            trace "No change"
        else
            trace "Updated $1 to $return_value_find_and_replace_text_in_text"
        fi
    fi
}

# arg 1 - Text in which all envirionment variable references will
# be replaced with actual values
#
find_and_replace_env_variables_in_text() {

    debug "ENTERED find_and_replace_env_variables_in_text text=$1"

    local holder=$1

    local temp_env_file=$(mktemp)

    # Output environment variables to the temp file
    env > $temp_env_file

    while read line; do

        # Remove leading and trailing space chars, as well as windows line endings (\r)
        local kv_pair=$(echo $line | sed -e 's/^\s*//g' -e 's/*\s$//g' -e 's/\r$//')

        # Using delimiter `=`, split this, collect first part
        local pair_key=$(echo $kv_pair | cut -d= -f 1)

        # Using delimiter `=`, sfind_and_replace_env_variables_in_textplit this, collect second part
        local pair_val=$(echo $kv_pair | cut -d= -f 2)

        pair_key=$(to_reference_fmt $pair_key)

        find_and_replace_text_in_text $holder ${pair_key} "$pair_val"

        holder=$return_value_find_and_replace_text_in_text

    done < $temp_env_file

    rm -f $temp_env_file

    return_value_find_and_replace_env_variables_in_text=$holder

    debug "EXITING find_and_replace_env_variables_in_text return_value=$return_value_find_and_replace_env_variables_in_text"
}

# arg 1 - target file
# arg 2 - to-replace
# arg 3 - replacement
#
find_and_replace_text_in_file() {

    if [ -z ${3+x} ] || [ "${3}" == '' ]; then
        trace "Replacement not available for: ${2}"
    else
        #@TODO ensure replacement took place by searching for the variable that
        # was replaced
        sed -i "s^${2}^${3}^g" $1 \
            && trace "Updated all ${2} to ${3} in $1" \
            || trace "No change"
    fi
}

# arg 1 - Path to a file in which all envirionment variable references will
# be replaced with actual values
#
find_and_replace_env_variables_in_file() {

    debug "ENTERED find_and_replace_env_variables_in_file file='$1'"

    local temp_env_file=$(mktemp)

    # Output environment variables to the temp file
    env > $temp_env_file

    while read line; do

        # Remove leading and trailing space chars, as well as windows line endings (\r)
        local kv_pair=$(echo $line | sed -e 's/^\s*//g' -e 's/*\s$//g' -e 's/\r$//')

        # Using delimiter `=`, split this, collect first part
        local pair_key=$(echo $kv_pair | cut -d= -f 1)

        # Using delimiter `=`, split this, collect second part
        local pair_val=$(echo $kv_pair | cut -d= -f 2)

        pair_key=$(to_reference_fmt $pair_key)

        find_and_replace_text_in_file $1 ${pair_key} "$pair_val"

    done < $temp_env_file

    rm -f $temp_env_file
}

# arg 1 - target dir
# arg 2 - to-replace
# arg 3 - replacement
#
find_and_replace_text_in_dir() {

    debug "ENTERED find_and_replace_text_in_dir target-dir='$1', to-replace='$2', replacement='$3'"

    local tgt=$1
    if [[ ${tgt} == /* ]]; then tgt="${tgt:1}"; fi # remove first char
    if [[ ${tgt} == ./* ]]; then tgt="${tgt:2}"; fi # remove first 2 chars
    trace "Formatted $2 to $tgt"

    if [ -d "./$tgt" ]; then

        local files=$(find "./${tgt}" -type f)
        for item in ${files[*]}
        do

            local tgtname=$(echo ${item})

            find_and_replace_text_in_file $tgtname ${2} ${3}
        done

    else
        warn ": Directory not found. Find and replace will not be carried out for $tgt"
    fi
}

# arg 1 - Path to a file to act on
# arg 2 - A function which will be called for each path found listed in arg1,
#         passing in the path as argument to the function
#
act_on_file() {

    debug "ENTERED act_on_file path='$1', function='$2'"

    find_and_replace_env_variables_in_text $1

    local path=$return_value_find_and_replace_env_variables_in_text

    if [ -f "$path" ]; then

        trace "Calling $2 with argument $path"

        $2 $path

    elif [ -d "$path" ]; then

        local files=$(find "${path}" -type f)
        for item in ${files[*]}
        do

            local filepath=$(echo ${item})

            trace "Calling $2 with argument $filepath"

            $2 $filepath

        done

    else
        warn ": Not found: $path"
    fi
}

# arg 1 - A file containing a list of files/directories to act on
# arg 2 - A function which will be called for each path found listed in arg1,
#         passing in the path as argument to the function
#
act_on_files_listed_in_file() {

    debug "ENTERED act_on_files_listed_in_file file='$1', function='$2'"

    while read line; do

        # Remove leading and trailing spaces
        line=$(echo -e "${line}" | sed -e 's,^[[:space:]]*,,' -e 's,[[:space:]]*$,,')

        # Remove all spaces
#        line=$(echo -e "${line}" | tr -d '[:space:]')

        if [[ ${line} == \#* ]]; then
            trace "Skipping line: $line"
        else

            trace "Processing line: $line"

            act_on_file $line $2
        fi
    done < $1
}

custom_find_and_replace_variables_in_file() {

    debug "ENTERED custom_find_and_replace_variables_in_file file=$1"

    # We seperate these 2 from the rest to fulfill the following requirement:
    #
    # SITE_AUTHOR_SUMMARY must come before SITE_AUTHOR to avoid partial
    # replacement of SITE_AUTHOR_SUMMARY
    #
    local key=$(to_reference_fmt $SITE_AUTHOR_SUMMARY)
    find_and_replace_text_in_file $1 "${key}" "$SITE_AUTHOR_SUMMARY"

    key=$(to_reference_fmt $AWS_S3_BUCKET_NAME_PREFIX)
    find_and_replace_text_in_file $1 "${key}" "$AWS_S3_BUCKET_NAME_PREFIX"
}
