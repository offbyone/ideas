provider "aws" {
  profile = "me"
  region  = "us-west-2"
}

provider "aws" {
  alias  = "useast1"
  region = "us-east-1"
}

module "log_storage" {
  bucket       = "logs.ideas.offby1.net"
  s3_logs_path = "s3-log-"
  source       = "github.com/jetbrains-infra/terraform-aws-s3-bucket-for-logs"
}

variable "domain_name" {
  default = "ideas.offby1.net"
}

variable "s3_origin_id" {
  default = "S3-ideas.offby1.net"
}

variable "zone_id" {
  default = "ZKLLVJ5PA0AR4"
}

resource "aws_s3_bucket" "blog" {
  depends_on = [module.log_storage.bucket]
  bucket     = var.domain_name
  region     = "us-west-2"
  acl        = "public-read"
  policy     = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [{
    "Sid": "AddPerm",
    "Effect": "Allow",
    "Principal": "*",
    "Action": "s3:GetObject",
    "Resource": "arn:aws:s3:::${var.domain_name}/*"
  }]
}
EOF

  website {
    index_document = "index.html"
    error_document = "error.html"
  }

  logging {
    target_bucket = module.log_storage.bucket_id
    target_prefix = "s3-log-"
  }

  tags = {
    "Project" = "ideas.blog"
    "Domain"  = "offby1.net"
  }

}

resource "aws_s3_bucket" "wwwblog" {
  bucket = "www.${var.domain_name}"
  region = "us-west-2"
  acl    = "public-read"
  website {
    redirect_all_requests_to = var.domain_name
  }
  tags = {
    "Project" = "ideas.blog"
    "Domain"  = "offby1.net"
  }
}

resource "aws_cloudfront_distribution" "frontend" {
  depends_on = [aws_s3_bucket.blog]

  origin {
    custom_origin_config {
      http_port              = 80
      https_port             = 443
      origin_protocol_policy = "http-only"
      origin_ssl_protocols   = ["TLSv1", "TLSv1.1", "TLSv1.2"]
    }

    // Important to use this format of origin domain name, it is the only format that
    // supports S3 redirects with CloudFront
    domain_name = aws_s3_bucket.blog.bucket_domain_name
    // domain_name = "${var.bucket_name}.s3-website-${var.aws_region}.amazonaws.com"

    origin_id = var.s3_origin_id
    # origin_path = var.origin_path
  }

  enabled             = true
  http_version        = "http1.1"
  is_ipv6_enabled     = false
  default_root_object = "index.html"

  aliases = [
    "ideas.offby1.net"
  ]

  logging_config {
    bucket          = module.log_storage.bucket
    include_cookies = false
    prefix          = "cf-log-"
  }

  default_cache_behavior {
    allowed_methods  = ["GET", "HEAD"]
    cached_methods   = ["GET", "HEAD"]
    target_origin_id = var.s3_origin_id

    forwarded_values {
      query_string = false

      cookies {
        forward = "none"
      }
    }

    viewer_protocol_policy = "redirect-to-https"

    // Using CloudFront defaults, tune to liking
    min_ttl     = 0
    default_ttl = 86400
    max_ttl     = 31536000
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

  tags = {
    "Project" = "ideas.blog"
    "Domain"  = "offby1.net"
  }
}

resource "aws_acm_certificate" "certificate" {
  provider    = aws.useast1
  domain_name = var.domain_name
  tags = {
    "Project" = "ideas.blog"
    "Domain"  = "offby1.net"
    "Name"    = "ideas-offby1-net"
  }
}

resource "aws_route53_record" "blog" {
  zone_id = var.zone_id
  name    = var.domain_name
  type    = "CNAME"
  records = ["${aws_cloudfront_distribution.frontend.domain_name}."]
  ttl     = 1799
}

resource "aws_iam_user" "blog_deploy" {
  name = "${var.domain_name}_blog_deploy"
  path = "/s3/"
  tags = {
    "Project" = "ideas.blog"
    "Domain"  = "offby1.net"
  }

}

resource "aws_iam_access_key" "blog_deploy" {
  user = aws_iam_user.blog_deploy.name
}

resource "aws_iam_user_policy" "blog_deploy_rw" {
  name   = "${var.domain_name}_rw"
  user   = aws_iam_user.blog_deploy.name
  policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Action": [
      "s3:ListBucketMultipartUploads",
      "s3:ListBucket",
      "s3:GetBucketLocation",
      "cloudfront:CreateInvalidation"
    ],
    "Resource": [
      "arn:aws:s3:::${var.domain_name}",
      "${aws_cloudfront_distribution.frontend.arn}"
    ],
    "Condition": {}
  }, {
    "Effect": "Allow",
    "Action": [
      "s3:AbortMultipartUpload",
      "s3:DeleteObject",
      "s3:DeleteObjectVersion",
      "s3:GetObject",
      "s3:GetObjectAcl",
      "s3:GetObjectVersion",
      "s3:GetObjectVersionAcl",
      "s3:PutObject",
      "s3:PutObjectAcl",
      "s3:PutObjectAclVersion"
    ],
    "Resource": "arn:aws:s3:::${var.domain_name}/*",
    "Condition": {}
  }, {
    "Effect": "Allow",
    "Action": "s3:ListAllMyBuckets",
    "Resource": "*",
    "Condition": {}
  }
]
}
EOF
}
