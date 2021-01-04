# terraform-aws-codepipeline-slack-notifications

[![Github Actions](https://github.com/kjagiello/terraform-aws-codepipeline-slack-notifications/workflows/CI/badge.svg)](https://github.com/kjagiello/terraform-aws-codepipeline-slack-notifications/actions?workflow=CI)

A terraform module to set up Slack notifications for your AWS CodePipelines. Available through the [Terraform registry](https://registry.terraform.io/modules/kjagiello/codepipeline-slack-notifications/aws).

![image](https://user-images.githubusercontent.com/74944/71839994-b660bf00-30bc-11ea-8e5e-4d8850da6900.png)

## Usage

```hcl
resource "aws_codepipeline" "example" {
  // ...
}

module "codepipeline_notifications" {
  source  = "kjagiello/codepipeline-slack-notifications/aws"
  version = "1.0.0"

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

Beware that during the initial apply, it might fail with following error:

> Error: error creating codestar notification rule: ConfigurationException: AWS
> CodeStar Notifications could not create the AWS CloudWatch Events managed
> rule in your AWS account. If this is your first time creating a notification
> rule, the service-linked role for AWS CodeStar Notifications might not yet
> exist. Creation of this role might take up to 15 minutes. Until it exists,
> notification rule creation will fail. Wait 15 minutes, and then try again. If
> this is is not the first time you are creating a notification rule, there
> might be a problem with a network connection, or one or more AWS services
> might be experiencing issues. Verify your network connection and check to see
> if there are any issues with AWS services in your AWS Region before trying
> again.

This is due to this module using [AWS CodeStar](https://aws.amazon.com/codestar/)
for subscribing to the CodePipeline state changes. The first use of a CodeStar
resource automatically creates the required service-linked role, which
typically is nearly instantaneous. Just reapply your Terraform plan and you
should be good to go.

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
