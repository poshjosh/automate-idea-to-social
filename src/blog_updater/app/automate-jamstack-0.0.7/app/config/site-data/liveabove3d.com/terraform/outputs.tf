output "hostname" {
  value       = var.hostname
  description = "Bucket hostname"
}

output "s3_bucket_name" {
  value       = module.s3_website.s3_bucket_name
  description = "DNS record of website bucket"
}

output "s3_bucket_domain_name" {
  value       = module.s3_website.s3_bucket_domain_name
  description = "Name of of website bucket"
}

output "s3_bucket_arn" {
  value       = module.s3_website.s3_bucket_arn
  description = "Name of of website bucket"
}

output "s3_bucket_website_endpoint" {
  value       = module.s3_website.s3_bucket_website_endpoint
  description = "The website endpoint URL"
}

output "s3_bucket_website_domain" {
  value       = module.s3_website.s3_bucket_website_domain
  description = "The domain of the website endpoint"
}

output "s3_bucket_hosted_zone_id" {
  value       = module.s3_website.s3_bucket_hosted_zone_id
  description = "The Route 53 Hosted Zone ID for this bucket's region"
}

# The following outputs are adapted for www_subdomain from above
output "s3_bucket_www_name" {
  value       = aws_s3_bucket.www_subdomain[0].id
  description = "DNS record of website bucket"
}

output "s3_bucket_www_domain_name" {
  value       = aws_s3_bucket.www_subdomain[0].bucket_domain_name
  description = "Name of of website bucket"
}

output "s3_bucket_www_arn" {
  value       = aws_s3_bucket.www_subdomain[0].arn
  description = "ARN identifier of www subdomain website bucket"
}

output "s3_bucket_www_website_endpoint" {
  value       = aws_s3_bucket.www_subdomain[0].website_endpoint
  description = "The website endpoint URL"
}

output "s3_bucket_www_website_domain" {
  value       = aws_s3_bucket.www_subdomain[0].website_domain
  description = "The domain of www subdomain website endpoint"
}

output "s3_bucket_www_hosted_zone_id" {
  value       = aws_s3_bucket.www_subdomain[0].hosted_zone_id
  description = "The Route 53 Hosted Zone ID for the www subdomain bucket's region"
}
