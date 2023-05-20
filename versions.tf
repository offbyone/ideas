terraform {
  required_providers {
    aws = {
      source  = "aws"
      version = ">= 4.67.0"
    }
  }
  required_version = ">= 1.4"
}

provider "aws" {
  profile = "me"
  region  = "us-west-2"
}

provider "aws" {
  profile = "me"
  alias   = "useast1"
  region  = "us-east-1"
}
