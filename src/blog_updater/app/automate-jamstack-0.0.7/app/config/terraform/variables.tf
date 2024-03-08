variable "create_www_subdomain" {
  type        = bool
  description = "Whether a www subdomain should be created"
  default     = ${AWS_S3_CREATE_WWW_SUBDOMAIN}
}

# variable "bucket_name" {
#   type        = string
#   description = "Used by logs module. Bucket name. If provided, the bucket will be created with this name instead of generating the name from the context"
#   default     = "ajtz-1e1r13kyaqmn-bxd9821-49mkjz-9213.com.logs"
# }

variable "region" {
  type        = string
  description = "AWS region"
  default    = "${AWS_REGION}"
}

variable "hostname" {
  type        = string
  description = "Name of website bucket in `fqdn` format (e.g. `test.example.com`). IMPORTANT! Do not add trailing dot (`.`)"
  default     = "${AWS_S3_BUCKET_NAME}"
}

variable "parent_zone_name" {
  type        = string
  description = "Name of the hosted zone to contain the record"
  default     = "${AWS_S3_BUCKET_NAME}"
}

variable "versioning_enabled" {
  type        = bool
  description = "Enable or disable versioning"
  default     = true
}

variable "force_destroy" {
  type        = bool
  description = "Delete all objects from the bucket so that the bucket can be destroyed without error (e.g. `true` or `false`)"
  default     = true
}

variable "encryption_enabled" {
  type        = bool
  description = "When set to 'true' the resource will have AES256 encryption enabled by default"
  default     = false
}

variable "index_document" {
  type        = string
  description = "Amazon S3 returns this index document when requests are made to the root domain or any of the subfolders"
  default     = "index.html"
}

variable "error_document" {
  type        = string
  description = "An absolute path to the document to return in case of a 4XX error"
  default     = "404.html"
}

# The following variables are used by module dns_www

variable "parent_zone_id" {
  type        = string
  description = "ID of the hosted zone to contain this record  (or specify `parent_zone_name`)"
  default     = "${AWS_HOSTED_ZONE_ID}"
}