module "subscription_label" {
  source  = "cloudposse/label/null"
  version = "0.25.0"

  attributes = ["pipeline", "updates"]

  context = module.this.context
}

resource "aws_sns_topic" "pipeline_updates" {
  # tfsec:ignore:AWS016
  name = module.subscription_label.id
  tags = module.this.tags
}

resource "aws_sns_topic_subscription" "pipeline_updates" {
  topic_arn = aws_sns_topic.pipeline_updates.arn
  protocol  = "lambda"
  endpoint  = aws_lambda_function.pipeline_notification.arn
}

resource "aws_codestarnotifications_notification_rule" "pipeline_updates" {
  for_each       = { for pipeline in var.codepipelines : pipeline.name => pipeline.arn }
  detail_type    = "FULL"
  event_type_ids = var.event_type_ids
  name           = join("-", [each.key, module.this.name])
  resource       = each.value

  target {
    address = aws_sns_topic.pipeline_updates.arn
    type    = "SNS"
  }

  tags = module.this.tags
}

resource "aws_sns_topic_policy" "pipeline_updates" {
  arn    = aws_sns_topic.pipeline_updates.arn
  policy = data.aws_iam_policy_document.pipeline_updates_policy.json
}

data "aws_iam_policy_document" "pipeline_updates_policy" {
  statement {
    sid    = "codestar-notification"
    effect = "Allow"
    resources = [
      aws_sns_topic.pipeline_updates.arn
    ]

    principals {
      identifiers = [
        "codestar-notifications.amazonaws.com"
      ]
      type = "Service"
    }
    actions = [
      "SNS:Publish"
    ]
  }
}

data "archive_file" "notifier_package" {
  type        = "zip"
  source_file = "${path.module}/lambdas/notifier/notifier.py"
  output_path = "${path.module}/lambdas/notifier.zip"
}

resource "aws_lambda_function" "pipeline_notification" {
  filename         = "${path.module}/lambdas/notifier.zip"
  function_name    = module.this.id
  role             = aws_iam_role.pipeline_notification.arn
  runtime          = "python3.8"
  source_code_hash = data.archive_file.notifier_package.output_base64sha256
  handler          = "notifier.handler"
  timeout          = 10

  environment {
    variables = {
      SLACK_WEBHOOK_URL = var.slack_url
      SLACK_CHANNEL     = var.slack_channel
      SLACK_USERNAME    = var.slack_username
      SLACK_EMOJI       = var.slack_emoji
      ENVIRONMENT       = var.stage
    }
  }

  tags = module.this.tags

  depends_on = [
    aws_iam_role_policy_attachment.pipeline_notification,
    data.archive_file.notifier_package,
  ]
}

resource "aws_lambda_permission" "pipeline_notification" {
  statement_id  = "AllowExecutionFromSNS"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.pipeline_notification.function_name
  principal     = "sns.amazonaws.com"
  source_arn    = aws_sns_topic.pipeline_updates.arn
}

data "aws_iam_policy_document" "pipeline_notification_role" {
  statement {
    actions = ["sts:AssumeRole"]
    principals {
      identifiers = ["lambda.amazonaws.com"]
      type        = "Service"
    }
  }
}

resource "aws_iam_role" "pipeline_notification" {
  name = "${module.this.id}-pipeline-notification"

  assume_role_policy = data.aws_iam_policy_document.pipeline_notification_role.json

  tags = module.this.tags
}

data "aws_iam_policy_document" "pipeline_notification" {
  statement {
    actions = [
      "logs:CreateLogGroup",
      "logs:CreateLogStream",
      "logs:PutLogEvents"
    ]
    resources = [
      "arn:aws:logs:*:*:*"
    ]
  }

  statement {
    actions = [
      "codepipeline:GetPipelineExecution"
    ]
    resources = var.codepipelines.*.arn
  }

  statement {
    actions = [
      "iam:PassRole"
    ]
    resources = [
      aws_iam_role.pipeline_notification.arn
    ]
  }
}

resource "aws_iam_policy" "pipeline_notification" {
  name        = "${module.this.id}-pipeline-notification"
  path        = "/"
  description = "IAM policy for the Slack notification lambda"

  policy = data.aws_iam_policy_document.pipeline_notification.json

  tags = module.default_label.tags
}

resource "aws_iam_role_policy_attachment" "pipeline_notification" {
  role       = aws_iam_role.pipeline_notification.name
  policy_arn = aws_iam_policy.pipeline_notification.arn
}
