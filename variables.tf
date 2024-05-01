variable "codepipelines" {
  type        = list(any)
  description = "CodePipeline resources that should trigger Slack notifications"
}

variable "slack_url" {
  type        = string
  description = "Slack webhook URL for deploy notifications"
}

variable "slack_channel" {
  type        = string
  description = "A slack channel to send the deployment notifications to"
}

variable "slack_username" {
  type        = string
  description = "The name of the user that sends the notifications"
  default     = "Deploy Bot"
}

variable "slack_emoji" {
  type        = string
  description = "The emoji avatar of the user that sends the notifications"
  default     = ":rocket:"
}

variable "pipeline_event_type_ids" {
  type        = list(string)
  description = "The list of pipeline events to trigger a notification on"
  default = [
    "started",
    "failed",
    "canceled",
    "resumed",
    "succeeded",
    "superseded"
  ]

  validation {
    condition = length(
      setsubtract(var.pipeline_event_type_ids, [
        "started",
        "failed",
        "canceled",
        "resumed",
        "succeeded",
        "superseded"
      ])
    ) == 0
    error_message = <<-EOF
    Invalid event type IDs found.
    Allowed type IDs: started, failed, canceled, resumed, succeeded, superseded.
    EOF
  }
}

variable "approval_event_type_ids" {
  type        = list(string)
  description = "The list of pipeline events to trigger a notification on"
  default = [
    "started",
    "succeeded",
    "failed",
  ]

  validation {
    condition = length(
      setsubtract(var.approval_event_type_ids, [
        "started",
        "succeeded",
        "failed",
      ])
    ) == 0
    error_message = <<-EOF
    Invalid event type IDs found.
    Allowed type IDs: started, succeeded, failed.
    EOF
  }
}

variable "lambda_runtime" {
  type        = string
  description = "The runtime to use for the lambda function"
  default     = "python3.12"
}
