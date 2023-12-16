provider "aws" {
  region = "eu-west-1"
}

module "codepipeline_notifications" {
  source = "../../"

  name          = "codepipeline-notifications"
  namespace     = "test"
  stage         = "test"
  slack_url     = var.slack_url
  slack_channel = var.slack_channel
  codepipelines = [
    aws_codepipeline.codepipeline,
  ]
}

resource "aws_codepipeline" "codepipeline" {
  name     = "notifications-test-pipeline"
  role_arn = aws_iam_role.codepipeline_role.arn

  artifact_store {
    location = aws_s3_bucket.artifact_bucket.bucket
    type     = "S3"
  }

  stage {
    name = "Source"

    action {
      name             = "Source"
      category         = "Source"
      owner            = "AWS"
      provider         = "S3"
      version          = "1"
      output_artifacts = ["test"]

      configuration = {
        S3Bucket    = aws_s3_bucket.source_bucket.bucket
        S3ObjectKey = aws_s3_object.source_object.key
      }
    }
  }

  // Codepipeline requires at least two stages so we cheat here a bit in order
  // to keep this example simple
  stage {
    name = "Dummy"

    action {
      name             = "Approval"
      category         = "Approval"
      owner            = "AWS"
      provider         = "Manual"
      version          = "1"
      output_artifacts = []
    }
  }
}

resource "aws_s3_bucket" "artifact_bucket" {
  # tfsec:ignore:AWS002
  bucket = "notifications-test-artifact-bucket"
  acl    = "private"

  server_side_encryption_configuration {
    rule {
      apply_server_side_encryption_by_default {
        sse_algorithm = "AES256"
      }
    }
  }
}

resource "aws_s3_bucket" "source_bucket" {
  # tfsec:ignore:AWS002
  bucket = "notifications-test-source-bucket"
  acl    = "private"

  versioning {
    enabled = true
  }

  server_side_encryption_configuration {
    rule {
      apply_server_side_encryption_by_default {
        sse_algorithm = "AES256"
      }
    }
  }
}

resource "aws_s3_object" "source_object" {
  bucket  = aws_s3_bucket.source_bucket.bucket
  key     = "test"
  content = "test"
}

resource "aws_iam_role" "codepipeline_role" {
  name = "notifications-test-codepipeline-role"

  assume_role_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "codepipeline.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
EOF
}

resource "aws_iam_role_policy" "codepipeline_policy" {
  name = "codepipeline_policy"
  role = aws_iam_role.codepipeline_role.id

  policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect":"Allow",
      "Action": [
        "s3:GetObject",
        "s3:GetObjectVersion",
        "s3:GetBucketVersioning",
        "s3:PutObject"
      ],
      "Resource": [
        "${aws_s3_bucket.artifact_bucket.arn}",
        "${aws_s3_bucket.artifact_bucket.arn}/*",
        "${aws_s3_bucket.source_bucket.arn}",
        "${aws_s3_bucket.source_bucket.arn}/*"
      ]
    },
    {
      "Effect": "Allow",
      "Action": [
        "codebuild:BatchGetBuilds",
        "codebuild:StartBuild"
      ],
      "Resource": "*"
    }
  ]
}
EOF
}
