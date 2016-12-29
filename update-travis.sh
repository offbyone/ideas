#!/bin/sh

travis encrypt AWS_SECRET_ACCESS_KEY=$(terraform output blog_iam_user_aws_secret_key) --override --add env.global
travis encrypt AWS_ACCESS_KEY_ID=$(terraform output blog_iam_user_aws_access_key) --append --add env.global
