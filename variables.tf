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

variable "event_type_ids" {
  type        = list(string)
  description = "The list of event type to trigger a notification on"
  default = [
    "failed",
    "canceled",
    "started",
    "resumed",
    "succeeded",
    "superseded"
  ]

  validation {
    condition = length(
      setsubtract(var.event_type_ids, [
        "failed",
        "canceled",
        "started",
        "resumed",
        "succeeded",
        "superseded",
        "stopping",
        "stopped",
        "abandoned"
      ])
    ) == 0
    error_message = <<-EOF
    Invalid event type IDs found.
    Allowed type IDs: failed, canceled, started, resumed, succeeded, superseded.
    EOF
  }
}
