terraform {
  required_providers {
    archive = {
      source  = "hashicorp/archive"
      version = ">= 1.3"
    }
    aws = {
      source  = "hashicorp/aws"
      version = ">= 2.70"
    }
  }
  required_version = ">= 0.12"
}
