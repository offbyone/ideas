output "blog_iam_user_aws_access_key" {
  value = aws_iam_access_key.blog_deploy.id
}

output "blog_iam_user_aws_secret_key" {
  value = aws_iam_access_key.blog_deploy.secret
}
