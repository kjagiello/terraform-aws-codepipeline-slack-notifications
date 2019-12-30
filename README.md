# terraform-aws-codepipeline-slack-notifications

[![Github Actions](https://github.com/kjagiello/terraform-aws-codepipeline-slack-notifications/workflows/CI/badge.svg)](https://github.com/kjagiello/terraform-aws-codepipeline-slack-notifications/actions?workflow=CI)

A terraform module to set up Slack notifications for your AWS CodePipelines.

![image](https://user-images.githubusercontent.com/74944/71839994-b660bf00-30bc-11ea-8e5e-4d8850da6900.png)

## Usage

```hcl
resource "aws_codepipeline" "example" {
  // ...
}

module "codepipeline_notifications" {
  source  = "git::https://github.com/kjagiello/terraform-aws-codepipeline-slack-notifications"

  name          = "codepipeline-notifications"
  namespace     = "kjagiello"
  stage         = "sandbox"
  slack_url     = "https://hooks.slack.com/services/(...)"
  slack_channel = "#notifications"
  codepipelines = [
    aws_codepipeline.example,
  ]
}
```

<!-- BEGINNING OF PRE-COMMIT-TERRAFORM DOCS HOOK -->
## Inputs

| Name | Description | Type | Default | Required |
|------|-------------|:----:|:-----:|:-----:|
| attributes | List of attributes to add to label | list | `[]` | no |
| codepipelines | CodePipeline resources that should trigger Slack notifications | list | n/a | yes |
| name | Name \(unique identifier for app or service\) | string | n/a | yes |
| namespace | Namespace \(e.g. `skynet`\) | string | n/a | yes |
| slack\_channel | A slack channel to send the deployment notifications to | string | n/a | yes |
| slack\_emoji | The emoji avatar of the user that sends the notifications | string | `":rocket:"` | no |
| slack\_url | Slack webhook URL for deploy notifications | string | n/a | yes |
| slack\_username | The name of the user that sends the notifications | string | `"Deploy Bot"` | no |
| stage | Stage \(e.g. `prod`, `dev`, `staging`\) | string | n/a | yes |

<!-- END OF PRE-COMMIT-TERRAFORM DOCS HOOK -->
