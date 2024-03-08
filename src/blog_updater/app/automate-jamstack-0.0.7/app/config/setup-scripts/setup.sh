#!/bin/bash

# If variable doesn't start with forward slash prefix it with forward slash
[[ ${SITE_PAGES_DIR} == /* ]] || SITE_PAGES_DIR="/${SITE_PAGES_DIR}"
g_config_dir="./config"
g_scripts_dir="${g_config_dir}/setup-scripts"
g_data_dir="${g_config_dir}/site-data"
g_pandoc_template_file="$g_data_dir/pandoc-template.markdown"
g_site_data_dir="${g_data_dir}/${SITE_DIR_NAME}"
g_terraform_dir="${g_config_dir}/terraform"
g_site_terraform_dir="${g_site_data_dir}/terraform"
g_sites_dir="./sites"
g_site_dir="${g_sites_dir}/${SITE_DIR_NAME}"
g_site_assets_dir="${g_site_dir}${SITE_ASSETS_DIR}"

source ${g_scripts_dir}/configure-aws-cli.sh
source ${g_scripts_dir}/functions-find.sh
source ${g_scripts_dir}/functions-gatsby.sh
source ${g_scripts_dir}/functions-pages.sh
source ${g_scripts_dir}/functions-util.sh
source ${g_scripts_dir}/functions-yarn.sh

if [ "$VERBOSE" = true ]; then
    env
    debug "============================================"
fi

printloc

ensure_aws_cli_configured() {
    local aws_config_file="${HOME}/.aws/config"
    local aws_cred_file="${HOME}/.aws/credentials"
    if [ -f "$aws_config_file" ] && [ -f "$aws_cred_file" ]; then
        info "AWS CLI already configured"
    else
        info 'Configuring AWS CLI'
        chmod +x ${g_scripts_dir}/configure-aws-cli.sh
        /bin/bash ${g_scripts_dir}/configure-aws-cli.sh
    fi
}

ensure_aws_cli_configured

is_site_newly_imported=false

# Import the site from source
#
import_site() {

    info "Importing site from $1"

    if [ -z ${1+x} ] || [ "$1" == '' ]; then
        debug "A source for the site was not specified will use contents of directory: ${g_site_dir}"
    else

        if [ -d "${g_site_dir}" ]; then
            debug "Deleting ${g_site_dir}"
            rm -Rf "${g_site_dir}"
        fi

        local tmp_dir="${g_sites_dir}/temp"

        if [ -d "$tmp_dir" ]; then
            debug "Deleting ${tmp_dir}"
            rm -Rf $tmp_dir
        fi

        import ${1} ${tmp_dir}

        local pkg_json="${tmp_dir}/package.json"

        if [ -f "$pkg_json" ]; then
            find_and_replace_env_variables_in_file ${pkg_json}
        else
             debug "File not found: $pkg_json"
        fi

        local site_source=$tmp_dir
        if [[ ${tmp_dir} == /* ]]; then
            site_source="..$tmp_dir"
        elif [[ ${tmp_dir} == ./* ]]; then
            site_source=".$tmp_dir"
        else
            site_source=$tmp_dir
        fi

        (cd ${g_sites_dir} && (gatsby_new_site "${site_source}" && is_site_newly_imported=true))

        debug "Deleting ${tmp_dir}"

        rm -Rf ${tmp_dir}
    fi
}

is_site_already_imported=false
check_site_imported() {
    local site_node_modules_dir="${g_site_dir}/node_modules"
    if [ -d "$site_node_modules_dir" ]; then
        is_site_already_imported=true
    else
        is_site_already_imported=false;
    fi
    debug "Site was already imported: $is_site_already_imported"
}

check_site_imported

if [ "${is_site_already_imported}" = false ] || [ "$REFRESH_SITE" = true ]; then

    if [ -d "${g_site_dir}" ]; then
        debug "Deleting ${g_site_dir}"
        rm -Rf "${g_site_dir}"
    fi

    import_site ${SITE_SOURCE}
fi


if [ "$REFRESH_SITE_CACHE" = true ] && [ "$is_site_newly_imported" = false ]; then

    info "Refreshing site cache"

    site_cache_dir="${g_site_dir}/.cache"

    deleting_cache_msg="Deleting cache at $site_cache_dir"

    debug $deleting_cache_msg

    if [ -d "$site_cache_dir" ]; then
        (rm -Rf "$site_cache_dir" && "SUCCESS: $deleting_cache_msg" || "ERROR: $deleting_cache_msg");
    fi
fi

is_site_pages_already_imported=false
site_pages_loc="${g_site_dir}${SITE_PAGES_DIR}"
check_site_pages_imported() {
    if [ -d "$site_pages_loc" ] && [ "$(ls -A $site_pages_loc)" ]; then
        is_site_pages_already_imported=true
    else
        is_site_pages_already_imported=false;
    fi
    debug "Site pages are imported: $is_site_pages_already_imported"
}

import_site_pages() {

    check_site_pages_imported

    if [ "${is_site_pages_already_imported}" = false ] || [ "$REFRESH_SITE_PAGES" = true ]; then

        info "Importing site pages from ${SITE_PAGES_SOURCE} to ${site_pages_loc}"

        if [ -d "$site_pages_loc" ]; then
            debug "Removing directory: ${site_pages_loc}"
            rm -Rf "$site_pages_loc";
        fi

        if [ ! -d "${site_pages_loc}" ]; then
            debug "Creating directory: ${site_pages_loc}"
            mkdir -p ${site_pages_loc}
        fi

        import ${SITE_PAGES_SOURCE} ${site_pages_loc}
    fi
}

if [ "$is_site_newly_imported" = false ]; then
    import_site_pages
fi

find_and_replace_variables() {

    info "Updating configuration"

    local file="${g_scripts_dir}/list_of_files_containing_variables.txt"

    debug "Will find and replace all variables in files listed in $file"
    debug "BEGIN FIND AND REPLACE"
    debug "======================================================================"
    debug ""
    debug "Function to apply = custom_find_and_replace_variables_in_file"
    act_on_files_listed_in_file $file custom_find_and_replace_variables_in_file

    debug ""
    debug "Function to apply = find_and_replace_env_variables_in_file"
    act_on_files_listed_in_file $file find_and_replace_env_variables_in_file

    debug "END FIND AND REPLACE"
    debug "======================================================================"
}

find_and_replace_variables

# Init terraform and use it to automate the creation of amazon s3 bucket

terraform_ok=true
site_terraform_filename='/bucket-created.state'
site_terraform_file="${g_site_terraform_dir}${site_terraform_filename}"
site_tfstate_file="${g_site_terraform_dir}/terraform.tfstate"
if [ -f "${site_terraform_file}" ] || [ -f "$site_tfstate_file" ]; then
    virgin=false
else
    virgin=true;
fi

update_terraform_cfgs() {

    mkdir -p ${g_site_terraform_dir}

    if [ -z ${AWS_S3_BUCKET_NAME+x} ] || [ "$AWS_S3_BUCKET_NAME" == '' ]; then

        debug "An s3 bucket name was not specified. Will generate one"

        local epoch_time=$(date '+%s')
        local raw_name="${AWS_S3_BUCKET_NAME_PREFIX}-${SITE_DIR_NAME}-${epoch_time}"
        local polished_name=$(echo $raw_name | tr '[:upper:]' '[:lower:]')

        # Export this to our list of environtment variables
        export "AWS_S3_BUCKET_NAME=${polished_name}" \
            && bucketname_set=true || bucketname_set=false

        if [ "$bucketname_set" = true ]; then

            debug "SUCCESS: set AWS_S3_BUCKET_NAME = $AWS_S3_BUCKET_NAME"

            props_file="${g_site_dir}.env"

            debug "Updating $props_file with environment AWS_S3_BUCKET_NAME"

            # Update our persistent store with the updated list of environment
            # variables which should now contain AWS_S3_BUCKET_NAME
            env > $props_file && "SUCCESS: Saved bucket name" || "ERROR: Bucket name not saved"

        else
            error ": Not set- AWS_S3_BUCKET_NAME = $AWS_S3_BUCKET_NAME"
        fi
    else
        debug "Existing AWS_S3_BUCKET_NAME = $AWS_S3_BUCKET_NAME"
    fi

    if [ -z ${AWS_S3_BUCKET_NAME+x} ] || [ "$AWS_S3_BUCKET_NAME" == '' ]; then
        warn "Value not set for AWS_S3_BUCKET_NAME. S3 bucket will not be created"
        terraform_ok=false
    fi

    if [ "$terraform_ok" = true ]; then

        info "Updating terraform configuration"

        cp -R "${g_terraform_dir}/." ${g_site_terraform_dir}

        find_and_replace_variables

        debug "SUCCESS: Updated terraform configuration"
    else
        error ": Not updated - terraform configuration"
        exit 1
    fi
}

terraform_init() {
    (cd ${1} && terraform init)
}

terraform_apply() {
    (cd ${1} && (echo 'yes' | terraform apply))
}

create_or_update_s3_bucket() {

    printloc

    if [ "$virgin" = true ] || [ "$AWS_S3_UPDATE_BUCKET" = true ]; then

        info "Creating/Updating S3 bucket using terraform ${g_site_terraform_dir}"

        local msginit='Intializing s3 bucket provisioner'
        debug $msginit
        terraform_init ${g_site_terraform_dir} \
            && debug "SUCCESS: $msginit" || error ": $msginit"

        local msgapply='Creating/Updating s3 bucket'
        debug $msgapply
        local applied=false;
        terraform_apply ${g_site_terraform_dir} && applied=true || applied=false
        if [ "$applied" = true ]; then
            debug "SUCCESS: $msgapply"
            write_to_file 's3-bucket-created' ${g_site_terraform_dir} ${site_terraform_filename}
        else
            error ": $msgapply"
            exit 1
        fi
    fi
}

if [ "$PROFILE" == 'prod' ]; then

    update_terraform_cfgs

    if [ "$terraform_ok" = true ]; then create_or_update_s3_bucket; fi

    printloc
fi

update_pages() {

    local pagesdir=${g_site_dir}${SITE_PAGES_DIR}
    local backupdir="${g_site_dir}/backups${SITE_PAGES_DIR}"

    if [ -d "${pagesdir}" ]; then

        info "Updating pages"
      
        add_frontmatter_to_markdown ${pagesdir}
        update_markdown_links ${pagesdir} ${backupdir}

        if [ "$PAGE_ADD_TABLE_OF_CONTENT" = true ]; then
            add_tableofcontents_to_markdown ${pagesdir} $g_pandoc_template_file
        fi

        debug "Copying assets from ${pagesdir}/assets to ${g_site_assets_dir}"
        # The * should be outside the double quotes
        cp -Rf "${pagesdir}/assets"/* "${g_site_assets_dir}"
    fi
}

# Update pages
#
update_pages

info "Setting up site"

gatsby_setup

# @see https://medium.com/@kyle.galbraith/how-to-host-a-website-on-s3-without-getting-lost-in-the-sea-e2b82aa6cd38
# If your website domain is www.my-awesome-site.com, then your bucket name must
# be www.my-awesome-site.com
aws_cli_deploy() {

    # Resulting URL format:  http://<AWS_S3_BUCKET_NAME>.s3.<AWS_REGION>.amazonaws.com/
#    (aws s3 website s3://${AWS_S3_BUCKET_NAME}/ --index-document index.html --error-document error.html) \
#        && debug "SUCCESS configuring AWS s3 bucket ${AWS_S3_BUCKET_NAME} for website hosting" \
#        || error " configuring AWS s3 bucket ${AWS_S3_BUCKET_NAME} for website hosting" \

# If using this make sure you check the reference link above for policy JSON
#    aws s3api put-bucket-policy --bucket <AWS_S3_BUCKET_NAME> --policy file://policy.json

    # Map your domain name www.my-awesome-site.com, to your S3 website url
    # <AWS_S3_BUCKET_NAME>.s3.us-east-2.amazonaws.com. This mapping is often
    # referred to as a CNAME record inside of your Domain Name Servers (DNS) records.
    #
    # - Create a record for a host like www
    # - The record type must be CNAME (Canonical name)
    # - The value must be your S3 website url www.<AWS_S3_BUCKET_NAME>.s3.<AWS_REGION>.amazonaws.com

    ensure_aws_cli_configured

    # The command gatsby build will build your site locally, updating the public/*
    # files
    aws s3 cp ${g_site_dir}/public/ s3://${AWS_S3_BUCKET_NAME}/ --recursive
}

if [ "$PROFILE" == 'prod' ]; then
    info "Deploying site"
    aws_cli_deploy
fi