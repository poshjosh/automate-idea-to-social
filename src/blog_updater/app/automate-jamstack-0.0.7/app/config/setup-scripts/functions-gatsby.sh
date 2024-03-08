#!/bin/bash

source ${g_scripts_dir}/functions-util.sh

gatsby_new_site() {

    local msg="Importing site from ${1}"

    debug ${msg}

    # Piping the result of echo is like piping of enter key press
    (echo | gatsby new ${SITE_DIR_NAME} ${1} ) \
    && debug "SUCCESS: $msg" || (error ": $msg" && exit 1)
}

gatsby_clean() {
    if [ -d "${g_site_dir}" ]; then

        debug "Cleaning site"

        (cd ${g_site_dir} && gatsby clean)
    fi
}

# - Run a webserver on specified port on the local machine
# - Use nohup to ensure the web server keeps running even after script exits
# - & at the end so the web server runs in background; and the script can exit
# instead of waiting for the webserver
#
gatsby_develop() {

    debug "Publishing site to local web server at http://localhost:$APP_PORT"

    # @TODO try exec gatsby develop

    # Exited immediately. Site not reachable at localhost
#    nohup gatsby develop -H 0.0.0.0 -p ${APP_PORT} &

    # Blocks (i.e nothing after will execute till finishes)
    # Site up and running at localhost
#    nohup gatsby develop -H 0.0.0.0 -p ${APP_PORT}  WORKED .. but blocks.. nothing after executes
    (cd ${g_site_dir} && gatsby develop -H 0.0.0.0 -p ${APP_PORT}) # this blocks.. nothing after executes
}

gatsby_build() {
    local msg='Building site'
    debug $msg
    (cd ${g_site_dir} && npm run build && debug "SUCCESS: $msg" || error ": $msg")
}

gatsby_plugin_s3_deploy() {

    debug 'Publishing site to amazon s3'
    if [ "$VERBOSE" = true ]; then
        (cd ${g_site_dir} && npm run deploy -y)
    else
        (cd ${g_site_dir} && npm run deploy --silent -y)
    fi
    debug 'Done publishing site to amazon s3'
}

gatsby_setup() {

    printloc

    gatsby telemetry --disable

    local gatsby_node_module_dir="${g_site_dir}/node_modules/gatsby-cli"
    if [ -d "$gatsby_node_module_dir" ] && [ "$(ls -A ${gatsby_node_module_dir})" ]; then
        trace ""
    else
        warn " : Gatsby-cli not installed. Will attempt to install it"
        (cd ${g_site_dir} && pkgmgr_add "gatsby-cli") || exit 1
    fi

    if [ "$PROFILE" == 'prod' ]; then
        gatsby_build
    else
        gatsby_develop
    fi
}