terraform {
  required_providers {
    archive = {
      source  = "hashicorp/archive"
      version = "~> 2.1"
    }
    aws = {
      source  = "hashicorp/aws"
      version = "~> 3.33"
    }
  }
  required_version = ">= 0.12"
}
