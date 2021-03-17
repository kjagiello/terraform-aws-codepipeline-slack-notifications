variable "name" {
  type        = string
  description = "Name (unique identifier for app or service)"
}

variable "namespace" {
  type        = string
  description = "Namespace (e.g. `skynet`)"
}

variable "stage" {
  type        = string
  description = "Stage (e.g. `prod`, `dev`, `staging`)"
}

variable "attributes" {
  type        = list(any)
  description = "List of attributes to add to label"
  default     = []
}

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
  type        = list(any)
  description = "The list of event type to trigger a notification on"
  default = [
    "codepipeline-pipeline-pipeline-execution-failed",
    "codepipeline-pipeline-pipeline-execution-canceled",
    "codepipeline-pipeline-pipeline-execution-started",
    "codepipeline-pipeline-pipeline-execution-resumed",
    "codepipeline-pipeline-pipeline-execution-succeeded",
    "codepipeline-pipeline-pipeline-execution-superseded"
  ]
}
