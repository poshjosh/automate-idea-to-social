#!/bin/bash

source ${g_scripts_dir}/functions-util.sh

add_tableofcontents_to_markdown() {

    debug "Adding table of contents to all .md files in ${1}"

    local files=$(find ${1} -iname '*.md' -type f)

    for item in ${files[*]}
    do

        trace $item

        local fname=$(echo $item)

        trace "Adding table of contents to: $fname"

        local toc_heading=$PAGE_TABLE_OF_CONTENT_HEADING

        if [ -z "$2" ]; then
            pandoc -s --toc -o $fname $fname
        else
            if [ -z "$toc_heading" ] || [ "$toc_heading" == '' ]; then
                warn ". Property PAGE_TABLE_OF_CONTENT_HEADING not found. Heading will not be added to table of content"
                pandoc -s --toc -o $fname $fname
            else
                # Put values in quote for toc-title and template
                pandoc -s --toc --variable toc-title:"$toc_heading" --template="$2" -o $fname $fname
            fi
        fi
    done
}

convert_title_to_tags()  {
    local update=$(echo "$1" | sed -e "s/[-_,;:.]/ /g")
    update=$(echo $update | tr -s ' ')
    update=$(echo $update | sed -e "s/ /\", \"/g")
    update="[\"$update\"]"
    update="$update"
    echo "$update"
}

add_frontmatter() {

    trace "add_frontmatter $1"

    local mdate=$(extract_date $1)

    trace "Found date:  $mdate  in  $1"

    if [ -z "$mdate" ]; then
        # %y = time of last modification, %z = time of last change
        # date and time:  stat -c %y ${1}
        # date only:      stat -c %y ${1} | cut -d ' ' -f 1
        mdate=$(stat -c %z $1 | cut -d ' ' -f 1)
        trace "Using file last modification date for $1"
    else
        local prev=$mdate
        # Replace non digits with dash
        mdate=$(echo $mdate | sed -e 's,[_|\|/],-,g')
        trace " Fmtd date:  $prev  to  $mdate"
    fi

    local name_without_ext=$(basename $1 .md)

    # Convert: The-good,_bad--latest to: The good, bad - latest
    local mtitle=$(echo $name_without_ext | sed -e "s/[-|_]/ /g" -e "s/  / - /g")

    local mtags=$(convert_title_to_tags "$name_without_ext")

    local frontmatter="---\npath: \"${1}\"\ndate: \"${mdate}\"\ntitle: \"${mtitle}\"\ndescription: \"${SITE_NAME} - ${mtitle}\"\ntags: ${mtags}\nlang: \"en-us\"\n---\n\n"

    trace "Front matter: $frontmatter"
    #log "functions-pages Front matter: $frontmatter"

    sed -i "1s~^~${frontmatter}~" ${1} || error "Failed to add frontmatter"
}

# Arg 1 - The file to Search
# Arg 2 - The result to return if none
get_first_non_space_line() {
    local found_line=$2;
    while read line; do
        if [[ $line =~ [^[:space:]] ]]; then
            found_line=$line
            break
        fi
    done < ${1}
    echo $found_line
}

add_frontmatter_to_markdown() {

    debug "Adding frontmatter to all .md files in ${1}"

    local files=$(find ${1} -iname '*.md' -type f)

    for item in ${files[*]}
    do

        trace $item

#        add_frontmatter $item                                        FAILED

# In this case, both `cut` and `sed` acted on the entire content of the file
# rather than just the filename
#        (echo $item | add_frontmatter)                               FAILED

#        fname=$(echo $item)
#        has_frontmatter=$(file_has_frontmatter $fname)               FAILED
#        if [ "${has_frontmatter}" = true ]; then (add_frontmatter $fname); fi

        local fname=$(echo $item)

#        has_frontmatter=$(echo $item | file_has_frontmatter $fname)  FAILED

        # Regex '^---$' won't work for windows line endings (i.e CRLF)
        #
#        (cat $fname | grep -q -E -m 1 '^---') \

        # Double dashes -- tell grep no options after this point, this is because
        # grep could mistake a dash for an option like -v etc
        local first_line=$(get_first_non_space_line $fname '')
        (echo $first_line | grep -q -E -m 1 -- '^---\s*') \
            && found_frontmatter=true || found_frontmatter=false

        if [ "$found_frontmatter" = true ]; then
            trace "Found frontmatter in: $fname"
        else
            add_frontmatter $fname
        fi
    done
}

update_links() {

    debug "Updating $3 to $4 in all $2 files in ${1}"

    local files=$(find ${1} -iname "${2}" -type f)

    for item in ${files[*]}
    do

        trace $item

        local fname=$(echo $item)

#        printf "\nFile: %s\n" $fname

        (sed -i "s^${3}^${4}^g" $fname) \
            && trace "SUCCESS replaced $3 with $4 in $fname" \
            || trace "ERROR replacing $3 with $4 in $fname"

    done
}

update_markdown_links() {

    local src=$1
    local bak=$2

    if [ ! -d "$bak" ]; then

        debug "Creating directory: $bak"
        mkdir -p $bak

        debug "Copying contents of: $src to: $bak"
        cp -R "${src}/." ${bak}
    fi

    # [My Link](abc/def/ghi.html)  to [My Link](abc/def/ghi/)
    update_links ${src} '*.md' '\.html\b' '/'

    if [ ! -z ${SITE_URL+x} ] && [ "$SITE_URL" != '' ]; then
        update_links ${src} '*.md' "\b$SITE_URL" ''
    fi

    if [ ! -z ${SITE_LINKS_TO_REPLACE+x} ] && [ "$SITE_LINKS_REPLACEMENT" != '' ]; then
        update_links ${src} '*.md' "\b$SITE_LINKS_TO_REPLACE" "$SITE_LINKS_REPLACEMENT"
    fi
}
