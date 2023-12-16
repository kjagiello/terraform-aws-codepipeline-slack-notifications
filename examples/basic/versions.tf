terraform {
  required_providers {
    archive = {
      source  = "hashicorp/archive"
      version = "~> 2.1"
    }
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
  required_version = ">= 0.12"
}
