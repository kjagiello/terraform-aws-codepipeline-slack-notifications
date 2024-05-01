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
  version = "3.0.0"

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

# Module documentation

<!-- BEGINNING OF PRE-COMMIT-TERRAFORM DOCS HOOK -->
## Requirements

| Name | Version |
|------|---------|
| <a name="requirement_terraform"></a> [terraform](#requirement\_terraform) | >= 1.5 |
| <a name="requirement_archive"></a> [archive](#requirement\_archive) | >= 1.3 |
| <a name="requirement_aws"></a> [aws](#requirement\_aws) | >= 5.0 |

## Inputs

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| <a name="input_additional_tag_map"></a> [additional\_tag\_map](#input\_additional\_tag\_map) | Additional tags for appending to tags\_as\_list\_of\_maps. Not added to `tags`. | `map(string)` | `{}` | no |
| <a name="input_approval_event_type_ids"></a> [approval\_event\_type\_ids](#input\_approval\_event\_type\_ids) | The list of pipeline events to trigger a notification on | `list(string)` | <pre>[<br>  "started",<br>  "succeeded",<br>  "failed"<br>]</pre> | no |
| <a name="input_attributes"></a> [attributes](#input\_attributes) | Additional attributes (e.g. `1`) | `list(string)` | `[]` | no |
| <a name="input_codepipelines"></a> [codepipelines](#input\_codepipelines) | CodePipeline resources that should trigger Slack notifications | `list(any)` | n/a | yes |
| <a name="input_context"></a> [context](#input\_context) | Single object for setting entire context at once.<br>See description of individual variables for details.<br>Leave string and numeric variables as `null` to use default value.<br>Individual variable settings (non-null) override settings in context object,<br>except for attributes, tags, and additional\_tag\_map, which are merged. | `any` | <pre>{<br>  "additional_tag_map": {},<br>  "attributes": [],<br>  "delimiter": null,<br>  "enabled": true,<br>  "environment": null,<br>  "id_length_limit": null,<br>  "label_key_case": null,<br>  "label_order": [],<br>  "label_value_case": null,<br>  "name": null,<br>  "namespace": null,<br>  "regex_replace_chars": null,<br>  "stage": null,<br>  "tags": {}<br>}</pre> | no |
| <a name="input_delimiter"></a> [delimiter](#input\_delimiter) | Delimiter to be used between `namespace`, `environment`, `stage`, `name` and `attributes`.<br>Defaults to `-` (hyphen). Set to `""` to use no delimiter at all. | `string` | `null` | no |
| <a name="input_enabled"></a> [enabled](#input\_enabled) | Set to false to prevent the module from creating any resources | `bool` | `null` | no |
| <a name="input_environment"></a> [environment](#input\_environment) | Environment, e.g. 'uw2', 'us-west-2', OR 'prod', 'staging', 'dev', 'UAT' | `string` | `null` | no |
| <a name="input_id_length_limit"></a> [id\_length\_limit](#input\_id\_length\_limit) | Limit `id` to this many characters (minimum 6).<br>Set to `0` for unlimited length.<br>Set to `null` for default, which is `0`.<br>Does not affect `id_full`. | `number` | `null` | no |
| <a name="input_label_key_case"></a> [label\_key\_case](#input\_label\_key\_case) | The letter case of label keys (`tag` names) (i.e. `name`, `namespace`, `environment`, `stage`, `attributes`) to use in `tags`.<br>Possible values: `lower`, `title`, `upper`.<br>Default value: `title`. | `string` | `null` | no |
| <a name="input_label_order"></a> [label\_order](#input\_label\_order) | The naming order of the id output and Name tag.<br>Defaults to ["namespace", "environment", "stage", "name", "attributes"].<br>You can omit any of the 5 elements, but at least one must be present. | `list(string)` | `null` | no |
| <a name="input_label_value_case"></a> [label\_value\_case](#input\_label\_value\_case) | The letter case of output label values (also used in `tags` and `id`).<br>Possible values: `lower`, `title`, `upper` and `none` (no transformation).<br>Default value: `lower`. | `string` | `null` | no |
| <a name="input_lambda_runtime"></a> [lambda\_runtime](#input\_lambda\_runtime) | The runtime to use for the lambda function | `string` | `"python3.12"` | no |
| <a name="input_name"></a> [name](#input\_name) | Solution name, e.g. 'app' or 'jenkins' | `string` | `null` | no |
| <a name="input_namespace"></a> [namespace](#input\_namespace) | Namespace, which could be your organization name or abbreviation, e.g. 'eg' or 'cp' | `string` | `null` | no |
| <a name="input_pipeline_event_type_ids"></a> [pipeline\_event\_type\_ids](#input\_pipeline\_event\_type\_ids) | The list of pipeline events to trigger a notification on | `list(string)` | <pre>[<br>  "started",<br>  "failed",<br>  "canceled",<br>  "resumed",<br>  "succeeded",<br>  "superseded"<br>]</pre> | no |
| <a name="input_regex_replace_chars"></a> [regex\_replace\_chars](#input\_regex\_replace\_chars) | Regex to replace chars with empty string in `namespace`, `environment`, `stage` and `name`.<br>If not set, `"/[^a-zA-Z0-9-]/"` is used to remove all characters other than hyphens, letters and digits. | `string` | `null` | no |
| <a name="input_slack_channel"></a> [slack\_channel](#input\_slack\_channel) | A slack channel to send the deployment notifications to | `string` | n/a | yes |
| <a name="input_slack_emoji"></a> [slack\_emoji](#input\_slack\_emoji) | The emoji avatar of the user that sends the notifications | `string` | `":rocket:"` | no |
| <a name="input_slack_url"></a> [slack\_url](#input\_slack\_url) | Slack webhook URL for deploy notifications | `string` | n/a | yes |
| <a name="input_slack_username"></a> [slack\_username](#input\_slack\_username) | The name of the user that sends the notifications | `string` | `"Deploy Bot"` | no |
| <a name="input_stage"></a> [stage](#input\_stage) | Stage, e.g. 'prod', 'staging', 'dev', OR 'source', 'build', 'test', 'deploy', 'release' | `string` | `null` | no |
| <a name="input_tags"></a> [tags](#input\_tags) | Additional tags (e.g. `map('BusinessUnit','XYZ')` | `map(string)` | `{}` | no |

## Outputs

No outputs.
<!-- END OF PRE-COMMIT-TERRAFORM DOCS HOOK -->
