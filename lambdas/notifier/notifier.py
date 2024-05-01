import json
import logging
import os
import urllib
import urllib.request

import boto3

logging.getLogger().setLevel(logging.INFO)
logger = logging.getLogger(__name__)

STATE_COLORS = {
    "Deployment": {
        "STARTED": "#1a9edb",
        "SUCCEEDED": "#50ba32",
        "RESUMED": "#1a9edb",
        "FAILED": "#f02b1d",
        "CANCELED": "#919191",
        "SUPERSEDED": "#919191",
    },
    "Approval": {
        "STARTED": "#f5d142",
        "SUCCEEDED": "#50ba32",
        "FAILED": "#f02b1d",
    },
}


def get_codepipeline_client():
    return boto3.client("codepipeline")


def format_slack_attachment(
    *,
    pipeline_name: str,
    pipeline_state: str,
    execution_id: str,
    environment: str,
    region: str,
    action: str,
    revision_summary: str | None,
    revision_url: str | None,
) -> dict:
    execution_link = (
        f"<https://{region}.console.aws.amazon.com/codesuite/codepipeline/"
        f"pipelines/{pipeline_name}/executions/{execution_id}/timeline"
        f"?region={region}|{execution_id}>"
    )
    if revision_summary:
        revision_link = (
            f"\n\n<{revision_url}|View the changeset>" if revision_url else ""
        )
        revision = [
            {
                "title": "Code revision",
                "value": f"{revision_summary}{revision_link}",
            },
        ]
    else:
        revision = [
            {
                "title": "Code revision",
                "value": "Unknown",
            },
        ]
    return {
        "color": STATE_COLORS[action][pipeline_state],
        "fallback": format_slack_text(
            pipeline_name=pipeline_name,
            pipeline_state=pipeline_state,
            action=action,
        ).replace("*", ""),
        "fields": [
            {"title": "Pipeline", "value": pipeline_name},
            {"title": "Execution ID", "value": execution_link},
            {"title": "Environment", "value": environment.upper(), "short": True},
            {"title": "Region", "value": region, "short": True},
            *revision,
        ],
    }


def format_slack_text(*, pipeline_name: str, pipeline_state: str, action: str):
    if action == "Approval":
        if pipeline_state == "STARTED":
            return f"*Deployment* of *{pipeline_name}* is awaiting approval."
        elif pipeline_state == "FAILED":
            return f"*Deployment* of *{pipeline_name}* has been rejected."
        elif pipeline_state == "SUCCEEDED":
            return f"*Deployment* of *{pipeline_name}* has been approved."
    return f"*{action}* of *{pipeline_name}* has {pipeline_state.lower()}."


def build_slack_message_from_event(event):
    # Parse the event and extract relevant bits and pieces
    message = json.loads(event["Records"][0]["Sns"]["Message"])
    region = message["region"]
    pipeline_name = message["detail"]["pipeline"]
    pipeline_state = message["detail"]["state"]
    pipeline_action = message["detail"].get("action")
    execution_id = message["detail"]["execution-id"]

    # Retrieve extra information about the pipeline run
    codepipeline = get_codepipeline_client()
    pipeline_execution = codepipeline.get_pipeline_execution(
        pipelineName=pipeline_name, pipelineExecutionId=execution_id
    )["pipelineExecution"]
    revision = pipeline_execution["artifactRevisions"][0]
    revision_url = revision.get("revisionUrl")
    revision_summary = revision.get("revisionSummary")
    action = pipeline_action or "Deployment"

    # Build a message with an attachment with details
    text = format_slack_text(
        pipeline_name=pipeline_name,
        pipeline_state=pipeline_state,
        action=action,
    )
    attachment = format_slack_attachment(
        pipeline_name=pipeline_name,
        pipeline_state=pipeline_state,
        execution_id=execution_id,
        region=region,
        action=action,
        revision_summary=revision_summary,
        revision_url=revision_url,
        environment=os.environ["ENVIRONMENT"],
    )

    return {
        "channel": os.environ["SLACK_CHANNEL"],
        "username": os.environ["SLACK_USERNAME"],
        "icon_emoji": os.environ["SLACK_EMOJI"],
        "text": text,
        "attachments": [attachment],
    }


def send_slack_notification(payload: dict):
    params = json.dumps(payload).encode()
    req = urllib.request.Request(
        os.environ["SLACK_WEBHOOK_URL"],
        data=params,
        headers={"content-type": "application/json"},
    )
    response = urllib.request.urlopen(req)
    # TODO: better log message
    logging.info(
        "Slack has responded with code %d: %r.", response.getcode(), response.read()
    )
    return response


def handler(event: dict, context: dict):
    logging.info("Received an event: %r.", event)
    payload = build_slack_message_from_event(event)
    send_slack_notification(payload)
