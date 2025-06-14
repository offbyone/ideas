data "aws_caller_identity" "current" {}
data "aws_canonical_user_id" "current" {}

module "log_storage" {
  bucket        = "logs.ideas.offby1.net"
  s3_logs_path  = "s3-log-"
  cdn_logs_path = "cf-log-"
  readers       = [data.aws_caller_identity.current.account_id]
  source        = "github.com/offbyone/terraform-aws-s3-bucket-for-logs?ref=v0.7.3"
  tags          = local.tags
}

variable "website_domain" {
  type    = string
  default = "offby1.website"
}

variable "website_alternate_domain" {
  type    = string
  default = "offbyone.website"
}

variable "dotnet_subdomain" {
  type    = string
  default = "ideas.offby1.net"
}

variable "s3_origin_id" {
  type    = string
  default = "S3-ideas.offby1.net"
}

data "aws_route53_zone" "zone" {
  name = "offby1.net"
}

data "aws_route53_zone" "website" {
  name = "offby1.website"
}

data "aws_route53_zone" "offbyone-website" {
  name = "offbyone.website"
}

locals {
  zone_id_map = {
    "ideas.offby1.net" = data.aws_route53_zone.zone.zone_id
    "offby1.website"   = data.aws_route53_zone.website.zone_id
    "offbyone.website" = data.aws_route53_zone.offbyone-website.zone_id
  }
  domain_names = [
    var.dotnet_subdomain,
    var.website_domain,
    var.website_alternate_domain,
  ]
  domain_name           = var.website_domain
  alternate_domain_name = var.website_alternate_domain
  bucket_name           = var.dotnet_subdomain

  tags = {
    Project = "ideas.blog"
    Domain  = "offby1.net"
    Source  = "https://github.com/offbyone/ideas"
  }
}

resource "aws_s3_bucket" "blog" {
  depends_on = [module.log_storage.s3_logs_bucket]
  bucket     = local.bucket_name

  tags = local.tags
}

resource "aws_s3_bucket_acl" "blog" {
  bucket = aws_s3_bucket.blog.id
  access_control_policy {
    owner {
      id           = data.aws_canonical_user_id.current.id
      display_name = "offline"
    }
  }
}

resource "aws_s3_bucket_website_configuration" "blog" {
  bucket = aws_s3_bucket.blog.id

  index_document {
    suffix = "index.html"
  }
  error_document {
    key = "error.html"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "blog" {
  bucket = aws_s3_bucket.blog.id

  rule {
    bucket_key_enabled = false
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_cors_configuration" "blog" {
  bucket = aws_s3_bucket.blog.id

  cors_rule {
    allowed_headers = ["*"]
    allowed_methods = ["GET", "HEAD", ]
    allowed_origins = formatlist("https://%s", local.domain_names)
    expose_headers  = ["ETag"]
    max_age_seconds = 0
  }
}

resource "aws_s3_bucket_logging" "blog" {
  bucket        = aws_s3_bucket.blog.id
  target_bucket = module.log_storage.s3_logs_bucket
  target_prefix = module.log_storage.s3_logs_path
}

resource "aws_s3_bucket_public_access_block" "blog" {
  bucket = aws_s3_bucket.blog.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

data "aws_iam_policy_document" "policy" {
  statement {
    sid = "AllowCloudFrontServicePrincipal"
    principals {
      type        = "Service"
      identifiers = ["cloudfront.amazonaws.com"]
    }

    actions = ["s3:GetObject"]

    resources = ["${aws_s3_bucket.blog.arn}/*"]

    condition {
      test     = "StringEquals"
      variable = "AWS:SourceArn"
      values   = [aws_cloudfront_distribution.frontend.arn]
    }
  }

  statement {
    sid = "AllowDeploymentBucket"
    principals {
      type = "AWS"
      identifiers = [
        aws_iam_role.blog_deploy.arn,
        "arn:aws:iam::${data.aws_caller_identity.current.account_id}:root"
      ]
    }

    actions = [
      "s3:ListBucketMultipartUploads",
      "s3:ListBucket",
      "s3:GetBucketLocation",
    ]

    resources = [aws_s3_bucket.blog.arn]
  }

  statement {
    sid = "AllowDeploymentFiles"
    principals {
      type = "AWS"
      identifiers = [
        aws_iam_role.blog_deploy.arn,
        "arn:aws:iam::${data.aws_caller_identity.current.account_id}:root"
      ]
    }

    actions = [
      "s3:AbortMultipartUpload",
      "s3:DeleteObject",
      "s3:DeleteObjectVersion",
      "s3:GetObject",
      "s3:GetObjectAcl",
      "s3:GetObjectVersion",
      "s3:GetObjectVersionAcl",
      "s3:PutObject",
      "s3:PutObjectAcl",
    ]

    resources = ["${aws_s3_bucket.blog.arn}/*"]
  }
}

resource "aws_s3_bucket_policy" "policy" {
  bucket = aws_s3_bucket.blog.id
  policy = data.aws_iam_policy_document.policy.json
}


resource "aws_s3_bucket" "wwwblog" {
  bucket = "www.${local.bucket_name}"
  tags   = local.tags
}

resource "aws_s3_bucket_acl" "wwwblog" {
  bucket = aws_s3_bucket.wwwblog.id
  access_control_policy {
    grant {
      permission = "READ"
      grantee {
        type = "Group"
        uri  = "http://acs.amazonaws.com/groups/global/AllUsers"
      }
    }

    grant {
      permission = "FULL_CONTROL"
      grantee {
        id   = data.aws_canonical_user_id.current.id
        type = "CanonicalUser"
      }
    }

    owner {
      id           = data.aws_canonical_user_id.current.id
      display_name = "offline"
    }
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "wwwblog" {
  bucket = aws_s3_bucket.wwwblog.id
  rule {
    bucket_key_enabled = false
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_website_configuration" "wwwblog" {
  bucket = aws_s3_bucket.wwwblog.id
  redirect_all_requests_to {
    host_name = local.bucket_name
  }
}

resource "aws_cloudfront_distribution" "frontend" {
  depends_on = [aws_s3_bucket.blog]
  comment    = "offby1.website hosting"

  origin {
    // Important to use this format of origin domain name, it is the only format that
    // supports S3 redirects with CloudFront
    domain_name              = aws_s3_bucket.blog.bucket_domain_name
    origin_id                = var.s3_origin_id
    origin_access_control_id = aws_cloudfront_origin_access_control.blog.id
  }

  enabled             = true
  http_version        = "http1.1"
  is_ipv6_enabled     = false
  default_root_object = "index.html"

  aliases = local.domain_names

  logging_config {
    bucket          = module.log_storage.cdn_logs_bucket
    include_cookies = false
    prefix          = module.log_storage.cdn_logs_path
  }

  default_cache_behavior {
    allowed_methods            = ["GET", "HEAD"]
    cached_methods             = ["GET", "HEAD"]
    target_origin_id           = var.s3_origin_id
    cache_policy_id            = data.aws_cloudfront_cache_policy.none.id
    origin_request_policy_id   = data.aws_cloudfront_origin_request_policy.cors-s3.id
    response_headers_policy_id = data.aws_cloudfront_response_headers_policy.gnu.id

    viewer_protocol_policy = "redirect-to-https"

    // Using CloudFront defaults, tune to liking
    min_ttl     = 0
    default_ttl = 0
    max_ttl     = 0
  }

  price_class = "PriceClass_100"

  viewer_certificate {
    acm_certificate_arn      = aws_acm_certificate.certificate.arn
    ssl_support_method       = "sni-only"
    minimum_protocol_version = "TLSv1.1_2016"
  }

  restrictions {
    geo_restriction {
      restriction_type = "none"
    }
  }

  tags = local.tags
}

resource "aws_cloudfront_origin_access_control" "blog" {
  name                              = aws_s3_bucket.blog.bucket_domain_name
  description                       = "Access to ${local.bucket_name}"
  origin_access_control_origin_type = "s3"
  signing_behavior                  = "always"
  signing_protocol                  = "sigv4"
}

data "aws_cloudfront_cache_policy" "none" {
  name = "Managed-CachingDisabled"
}

data "aws_cloudfront_origin_request_policy" "cors-s3" {
  name = "Managed-CORS-S3Origin"
}

data "aws_cloudfront_response_headers_policy" "gnu" {
  name = "GNU"
}

resource "aws_acm_certificate" "certificate" {
  provider    = aws.useast1
  domain_name = local.domain_names[0]
  tags = merge(local.tags, {
    Name = "ideas-offby1-net"
  })

  validation_method = "DNS"

  subject_alternative_names = slice(local.domain_names, 1, length(local.domain_names))

  lifecycle {
    create_before_destroy = true
  }
}

resource "aws_route53_record" "cert_validation" {
  for_each = {
    for dvo in aws_acm_certificate.certificate.domain_validation_options : dvo.domain_name => {
      name    = dvo.resource_record_name
      record  = dvo.resource_record_value
      type    = dvo.resource_record_type
      zone_id = local.zone_id_map[dvo.domain_name]
    }
  }

  allow_overwrite = true
  name            = each.value.name
  type            = each.value.type
  zone_id         = each.value.zone_id
  records         = [each.value.record]
  ttl             = 60

}

resource "aws_acm_certificate_validation" "certificate" {
  provider                = aws.useast1
  certificate_arn         = aws_acm_certificate.certificate.arn
  validation_record_fqdns = [for record in aws_route53_record.cert_validation : record.fqdn]
}

resource "aws_route53_record" "blog" {
  zone_id = data.aws_route53_zone.website.zone_id
  name    = local.domain_name
  type    = "A"
  alias {
    name                   = aws_cloudfront_distribution.frontend.domain_name
    zone_id                = aws_cloudfront_distribution.frontend.hosted_zone_id
    evaluate_target_health = true
  }
}

resource "aws_route53_record" "offbyone-website" {
  zone_id = data.aws_route53_zone.offbyone-website.zone_id
  name    = local.alternate_domain_name
  type    = "A"

  alias {
    name                   = aws_cloudfront_distribution.frontend.domain_name
    zone_id                = aws_cloudfront_distribution.frontend.hosted_zone_id
    evaluate_target_health = true
  }
}

data "aws_iam_user" "me" {
  user_name = "chrisros"
}

data "aws_iam_openid_connect_provider" "github" {
  url = "https://token.actions.githubusercontent.com"
}

# OIDC provider policy document
# see https://docs.github.com/en/actions/deployment/security-hardening-your-deployments/configuring-openid-connect-in-amazon-web-services
data "aws_iam_policy_document" "deployer" {
  statement {
    effect = "Allow"
    principals {
      type = "AWS"
      identifiers = [
        data.aws_iam_user.me.arn
      ]
    }
    actions = ["sts:AssumeRole"]
  }

  statement {
    effect = "Allow"
    principals {
      type = "Federated"
      identifiers = [
        data.aws_iam_openid_connect_provider.github.arn
      ]
    }
    actions = ["sts:AssumeRoleWithWebIdentity"]
    condition {
      test     = "StringEquals"
      variable = "token.actions.githubusercontent.com:aud"
      values   = ["sts.amazonaws.com"]
    }
    condition {
      test     = "StringLike"
      variable = "token.actions.githubusercontent.com:sub"
      values   = ["repo:offbyone/ideas:*"]
    }
  }
}

resource "aws_iam_role" "blog_deploy" {
  name               = "ideas-deployer"
  tags               = local.tags
  assume_role_policy = data.aws_iam_policy_document.deployer.json
}

data "aws_iam_policy_document" "deploy" {
  statement {
    sid     = "AllowS3"
    effect  = "Allow"
    actions = ["s3:*"]
    resources = [
      "${aws_s3_bucket.blog.arn}/*",
      aws_s3_bucket.blog.arn
    ]
  }
  statement {
    sid     = "AllowCloudFront"
    effect  = "Allow"
    actions = ["cloudfront:CreateInvalidation"]
    resources = [
      aws_cloudfront_distribution.frontend.arn
    ]
  }
}

resource "aws_iam_role_policy" "cloudfront" {
  role   = aws_iam_role.blog_deploy.name
  policy = data.aws_iam_policy_document.deploy.json
}
