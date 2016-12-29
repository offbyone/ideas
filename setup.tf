provider "aws" {
  access_key = "${var.aws_access_key}"
  secret_key = "${var.aws_secret_key}"
  region = "us-west-2"
}

variable "domain_name" {
  default = "ideas.offby1.net"
}

# resource "aws_route53_zone" "primary" {
#   name = "${var.domain_name}"
# }

resource "aws_s3_bucket" "blog" {
  bucket = "${var.domain_name}"
  region = "us-west-2"
  acl = "public-read"
  policy = <<EOF
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
}

resource "aws_s3_bucket" "wwwblog" {
  bucket = "www.${var.domain_name}"
  region = "us-west-2"
  acl = "public-read"
  website {
    redirect_all_requests_to = "${var.domain_name}"
  }
}


# resource "aws_route53_record" "blog" {
#   zone_id = "${aws_route53_zone.primary.zone_id}"
#   name = "${var.domain_name}"
#   type = "A"
#   alias {
#     name = "${aws_s3_bucket.blog.website_domain}"
#     zone_id = "${aws_s3_bucket.blog.hosted_zone_id}"
#     evaluate_target_health = true
#   }
# }

# resource "aws_route53_record" "wwwblog" {
#   zone_id = "${aws_route53_zone.primary.zone_id}"
#   name = "www.${var.domain_name}"
#   type = "A"
#   alias {
#     name = "${aws_s3_bucket.wwwblog.website_domain}"
#     zone_id = "${aws_s3_bucket.wwwblog.hosted_zone_id}"
#     evaluate_target_health = true
#   }
# }

resource "aws_iam_user" "blog_deploy" {
  name = "${var.domain_name}_blog_deploy"
  path = "/s3/"
}

resource "aws_iam_access_key" "blog_deploy" {
  user = "${aws_iam_user.blog_deploy.name}"
}

resource "aws_iam_user_policy" "blog_deploy_rw" {
  name = "${var.domain_name}_rw"
  user = "${aws_iam_user.blog_deploy.name}"
  policy = <<EOF
{
  "Statement": [{
    "Effect": "Allow",
    "Action": [
      "s3:ListBucket",
      "s3:GetBucketLocation",
      "s3:ListBucketMultipartUploads"
    ],
    "Resource": "arn:aws:s3:::${var.domain_name}",
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
  }]
}
EOF
}
