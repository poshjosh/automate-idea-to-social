provider "aws" {

  # profile refers to the user profile we are using to connect to AWS
  # It is available after installing AWS CLI and running command aws configure

  profile = "default"
  region  = var.region
}

# Adapted from https://github.com/cloudposse/terraform-aws-s3-website/blob/0.18.0/examples/complete/main.tf
module "s3_website" {
  source = "git::https://github.com/cloudposse/terraform-aws-s3-website.git?ref=tags/0.18.0"
  hostname = var.hostname
  parent_zone_name = var.parent_zone_name
  force_destroy = var.force_destroy
  logs_enabled = false
}

# Adapted from https://github.com/cloudposse/terraform-aws-s3-website/blob/0.18.0/main.tf
resource "aws_s3_bucket_public_access_block" "www_s3_allow_public_access" {
  # The bucket used for a public static website.
  #bridgecrew:skip=BC_AWS_S3_19:Skipping `Ensure S3 bucket has block public ACLS enabled`
  #bridgecrew:skip=BC_AWS_S3_20:Skipping `Ensure S3 Bucket BlockPublicPolicy is set to True`
  #bridgecrew:skip=BC_AWS_S3_21:Skipping `Ensure S3 bucket IgnorePublicAcls is set to True`
  #bridgecrew:skip=BC_AWS_S3_22:Skipping `Ensure S3 bucket RestrictPublicBucket is set to True`
  bucket        = aws_s3_bucket.www_subdomain[0].id

  block_public_acls       = false
  block_public_policy     = false
  ignore_public_acls      = false
  restrict_public_buckets = false
  count = var.create_www_subdomain ? 1 : 0
}

# Adapted from https://github.com/cloudposse/terraform-aws-s3-website/blob/0.18.0/main.tf
resource "aws_s3_bucket_ownership_controls" "www_s3_bucket_ownership_controls" {
  bucket        = aws_s3_bucket.www_subdomain[0].id
  rule {
    object_ownership = "ObjectWriter"
  }
  count = var.create_www_subdomain ? 1 : 0
}

# Adapted from https://github.com/cloudposse/terraform-aws-s3-website/blob/0.18.0/main.tf
# The s3 bucket website module above creates only one s3 bucket.
# When we tried to use it twice(to create 2 buckets one main other www subdomain),
# terraform complained that we are trying to create a bucket we already owned.
# The bucket name give i.e 'default' is the bucket name specified in the module
# Hence we can't use the module to create 2 buckets at once.
resource "aws_s3_bucket" "www_subdomain" {
  bucket        = "www.${var.hostname}"
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

# Adapted from https://github.com/cloudposse/terraform-aws-s3-website/blob/0.18.0/main.tf
resource "aws_s3_bucket_policy" "www_subdomain" {
  bucket = aws_s3_bucket.www_subdomain[0].id
  policy = data.aws_iam_policy_document.www_subdomain[0].json

  depends_on = [aws_s3_bucket_public_access_block.www_s3_allow_public_access[0]]
  count      = var.create_www_subdomain ? 1 : 0
}

# Adapted from https://github.com/cloudposse/terraform-aws-s3-website/blob/0.18.0/main.tf
data "aws_iam_policy_document" "www_subdomain" {
  statement {
    actions = ["s3:GetObject"]

    resources = ["${aws_s3_bucket.www_subdomain[0].arn}/*"]

    principals {
      type        = "AWS"
      identifiers = ["*"]
    }
  }
  count      = var.create_www_subdomain ? 1 : 0
}

# Adapted from https://github.com/cloudposse/terraform-aws-route53-alias/blob/0.13.0/examples/complete/main.tf
module "dns_www" {
  source           = "git::https://github.com/cloudposse/terraform-aws-route53-alias.git?ref=tags/0.13.0"
  aliases          = compact([signum(length(var.parent_zone_id)) == 1 ? "www.${var.hostname}" : ""])
  parent_zone_id   = var.parent_zone_id
  target_dns_name  = aws_s3_bucket.www_subdomain[0].website_domain
  target_zone_id   = aws_s3_bucket.www_subdomain[0].hosted_zone_id
  enabled          = var.create_www_subdomain
}
