provider "aws" {

  # profile refers to the user profile we are using to connect to AWS
  # It is available after installing AWS CLI and running command aws configure

  profile = "default"
  region  = var.region
}

module "website" {
  source = "git::https://github.com/cloudposse/terraform-aws-s3-website.git?ref=tags/0.9.0"
  region = var.region
  name = var.name
  hostname = var.hostname
  parent_zone_id = var.parent_zone_id
  force_destroy = var.force_destroy
  versioning_enabled = var.versioning_enabled
  index_document = var.index_document
  error_document = var.error_document
}

# Extracted from https://github.com/cloudposse/terraform-aws-s3-website.git?ref=tags/0.9.0
# The s3 bucket website module above creates only one s3 bucket.
# When we tried to use it twice(to create 2 buckets one main other www subdomain),
# terraform complained that we are trying to create a bucket we already owned.
# The bucket name give i.e 'default' is the bucket name specified in the module
# Hence we can't use the module to create 2 buckets at once.
resource "aws_s3_bucket" "www_subdomain" {
  bucket        = "www.${var.hostname}"
  acl           = "public-read"
  region        = var.region
  force_destroy = var.force_destroy

  website {
    redirect_all_requests_to = var.hostname
  }
  tags = {
    Name = "www.${var.hostname}"
  }
  cors_rule {
    allowed_headers = ["*"]
    allowed_methods = ["GET"]
    allowed_origins = ["*"]
    expose_headers  = ["ETag"]
    max_age_seconds = 3000
  }
  versioning {
    enabled = var.versioning_enabled
  }
  count = var.create_www_subdomain ? 1 : 0
}

output "s3_bucket_www_domain" {
  value       = aws_s3_bucket.www_subdomain[0].website_domain
  description = "The domain of www subdomain website endpoint"
}

output "s3_bucket_www_hosted_zone_id" {
  value       = aws_s3_bucket.www_subdomain[0].hosted_zone_id
  description = "The Route 53 Hosted Zone ID for the www subdomain bucket's region"
}

# Extracted from https://github.com/cloudposse/terraform-aws-s3-website.git?ref=tags/0.9.0
module "dns_www" {
  source           = "git::https://github.com/cloudposse/terraform-aws-route53-alias.git?ref=tags/0.3.0"
  aliases          = compact([signum(length(var.parent_zone_id)) == 1 ? "www.${var.hostname}" : ""])
  parent_zone_id   = var.parent_zone_id
  target_dns_name  = aws_s3_bucket.www_subdomain[0].website_domain
  target_zone_id   = aws_s3_bucket.www_subdomain[0].hosted_zone_id
  enabled          = var.create_www_subdomain
}
