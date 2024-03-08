#!/bin/bash

source ${g_scripts_dir}/functions-util.sh

if [ -z ${AWS_OUTPUT+x} ]; then
    debug "Skipping AWS_OUTPUT"
else
    debug 'Configuring AWS_OUTPUT'
    aws configure set default.output $AWS_OUTPUT && debug "SUCCESS" || error ""
fi
if [ -z ${AWS_REGION+x} ]; then
    debug "Skipping AWS_REGION"
else
    debug 'Configuring AWS_REGION'
    aws configure set default.region $AWS_REGION && debug "SUCCESS" || error ""
fi
if [ -z ${AWS_ACCESS_KEY+x} ]; then
    debug "Skipping AWS_ACCESS_KEY"
else
    debug 'Configuring AWS_ACCESS_KEY'
    aws configure set default.aws_access_key_id $AWS_ACCESS_KEY && debug "SUCCESS" || error ""
fi
if [ -z ${AWS_SECRET_KEY+x} ]; then
    debug "Skipping AWS_SECRET_KEY"
else
    debug 'Configuring AWS_SECRET_KEY'
    aws configure set default.aws_secret_access_key $AWS_SECRET_KEY && debug "SUCCESS" || error ""
fi

if [ "$VERBOSE" = true ]; then aws configure list; fi
