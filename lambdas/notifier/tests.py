import json
import os
import unittest
from copy import deepcopy
from unittest import mock

import boto3
from botocore.stub import Stubber

import notifier

ENVIRONMENT = {
    "SLACK_CHANNEL": "#notifications",
    "SLACK_USERNAME": "Mr. Robot",
    "SLACK_EMOJI": ":rocket:",
    "SLACK_WEBHOOK_URL": "https://slack.com/webhook",
    "ENVIRONMENT": "qa",
}

TEST_PIPELINE_UPDATE = {
    "version": "0",
    "id": "81ff0678-5b31-cfc8-0ac7-df8664cd764a",
    "detail-type": "CodePipeline Pipeline Execution State Change",
    "source": "aws.codepipeline",
    "account": "203144576027",
    "time": "2019-12-27T23:47:58Z",
    "region": "eu-west-1",
    "resources": ["arn:aws:codepipeline:eu-west-1:203144576027:kjagiello-qa-homepage"],
    "detail": {
        "pipeline": "kjagiello-qa-homepage",
        "execution-id": "0aeb1e48-4de1-4d3c-8815-4a8a701b1fcc",
        "state": "STARTED",
        "version": 20.0,
    },
}


def pipeline_approval(state):
    return {
        "version": "0",
        "id": "81ff0678-5b31-cfc8-0ac7-df8664cd764a",
        "detail-type": "CodePipeline Action Execution State Change",
        "source": "aws.codepipeline",
        "account": "203144576027",
        "time": "2019-12-27T23:47:58Z",
        "region": "eu-west-1",
        "resources": [
            "arn:aws:codepipeline:eu-west-1:203144576027:kjagiello-qa-homepage"
        ],
        "detail": {
            "pipeline": "kjagiello-qa-homepage",
            "execution-id": "0aeb1e48-4de1-4d3c-8815-4a8a701b1fcc",
            "state": state,
            "version": 20.0,
            "action": "Approval",
        },
    }


def wrap_event(event):
    return {
        "Records": [
            {
                "EventSource": "aws:sns",
                "EventVersion": "1.0",
                "EventSubscriptionArn": (
                    "arn:aws:sns:eu-west-1:203144576027"
                    ":kjagiello-qa-codepipeline-notifications-test-pipeline-updates"
                    ":6f7fa819-b7ae-499c-ad67-9aa4fc7a732d"
                ),
                "Sns": {
                    "Type": "Notification",
                    "MessageId": "a32e2bde-ed90-5cbf-87ba-7d5e77e56761",
                    "TopicArn": (
                        "arn:aws:sns:eu-west-1:203144576027"
                        ":kjagiello-qa-codepipeline-notifications-test-pipeline-updates"
                    ),
                    "Subject": None,
                    "Message": json.dumps(event),
                    "Timestamp": "2019-12-27T23:48:05.126Z",
                    "SignatureVersion": "1",
                    "Signature": "signature",
                    "SigningCertUrl": "https://sns.eu-west-1.amazonaws.com/...",
                    "UnsubscribeUrl": "https://sns.eu-west-1.amazonaws.com/...",
                    "MessageAttributes": {},
                },
            }
        ]
    }


PIPELINE_EXECUTION = {
    "service_response": {
        "pipelineExecution": {
            "pipelineName": "kjagiello-test-pipeline",
            "pipelineVersion": 20,
            "pipelineExecutionId": "7911f31b-9991-42c2-90db-a5c20ad62b82",
            "status": "Succeeded",
            "artifactRevisions": [
                {
                    "name": "source_output",
                    "revisionId": "98732042443d83df6cdc60d1f0bd5bf708e39",
                    "revisionSummary": "commit message",
                    "revisionUrl": "http://foo.bar",
                }
            ],
        }
    },
    "expected_params": {
        "pipelineName": "kjagiello-qa-homepage",
        "pipelineExecutionId": "0aeb1e48-4de1-4d3c-8815-4a8a701b1fcc",
    },
}

TEST_MATRIX = [
    (
        TEST_PIPELINE_UPDATE,
        {
            "channel": "#notifications",
            "username": "Mr. Robot",
            "icon_emoji": ":rocket:",
            "text": "*Deployment* of *kjagiello-qa-homepage* has started.",
            "attachments": [
                {
                    "color": "#1a9edb",
                    "fallback": "Deployment of kjagiello-qa-homepage has started.",
                    "fields": [
                        {"title": "Pipeline", "value": "kjagiello-qa-homepage"},
                        {
                            "title": "Execution ID",
                            "value": (
                                "<https://eu-west-1.console.aws.amazon.com/"
                                "codesuite/codepipeline/pipelines/kjagiello-"
                                "qa-homepage/executions/0aeb1e48-4de1-4d3c-"
                                "8815-4a8a701b1fcc/timeline?region=eu-west-1|"
                                "0aeb1e48-4de1-4d3c-8815-4a8a701b1fcc>"
                            ),
                        },
                        {"title": "Environment", "value": "QA", "short": True},
                        {"title": "Region", "value": "eu-west-1", "short": True},
                        {
                            "title": "Code revision",
                            "value": (
                                "commit message\n\n"
                                "<http://foo.bar|View the changeset>"
                            ),
                        },
                    ],
                }
            ],
        },
    ),
    (
        pipeline_approval("STARTED"),
        {
            "channel": "#notifications",
            "username": "Mr. Robot",
            "icon_emoji": ":rocket:",
            "text": "*Deployment* of *kjagiello-qa-homepage* is awaiting approval.",
            "attachments": [
                {
                    "color": "#f5d142",
                    "fallback": "Deployment of kjagiello-qa-homepage is awaiting approval.",
                    "fields": [
                        {"title": "Pipeline", "value": "kjagiello-qa-homepage"},
                        {
                            "title": "Execution ID",
                            "value": (
                                "<https://eu-west-1.console.aws.amazon.com/"
                                "codesuite/codepipeline/pipelines/kjagiello-"
                                "qa-homepage/executions/0aeb1e48-4de1-4d3c-"
                                "8815-4a8a701b1fcc/timeline?region=eu-west-1|"
                                "0aeb1e48-4de1-4d3c-8815-4a8a701b1fcc>"
                            ),
                        },
                        {"title": "Environment", "value": "QA", "short": True},
                        {"title": "Region", "value": "eu-west-1", "short": True},
                        {
                            "title": "Code revision",
                            "value": (
                                "commit message\n\n"
                                "<http://foo.bar|View the changeset>"
                            ),
                        },
                    ],
                }
            ],
        },
    ),
    (
        pipeline_approval("SUCCEEDED"),
        {
            "channel": "#notifications",
            "username": "Mr. Robot",
            "icon_emoji": ":rocket:",
            "text": "*Deployment* of *kjagiello-qa-homepage* has been approved.",
            "attachments": [
                {
                    "color": "#50ba32",
                    "fallback": "Deployment of kjagiello-qa-homepage has been approved.",
                    "fields": [
                        {"title": "Pipeline", "value": "kjagiello-qa-homepage"},
                        {
                            "title": "Execution ID",
                            "value": (
                                "<https://eu-west-1.console.aws.amazon.com/"
                                "codesuite/codepipeline/pipelines/kjagiello-"
                                "qa-homepage/executions/0aeb1e48-4de1-4d3c-"
                                "8815-4a8a701b1fcc/timeline?region=eu-west-1|"
                                "0aeb1e48-4de1-4d3c-8815-4a8a701b1fcc>"
                            ),
                        },
                        {"title": "Environment", "value": "QA", "short": True},
                        {"title": "Region", "value": "eu-west-1", "short": True},
                        {
                            "title": "Code revision",
                            "value": (
                                "commit message\n\n"
                                "<http://foo.bar|View the changeset>"
                            ),
                        },
                    ],
                }
            ],
        },
    ),
    (
        pipeline_approval("FAILED"),
        {
            "channel": "#notifications",
            "username": "Mr. Robot",
            "icon_emoji": ":rocket:",
            "text": "*Deployment* of *kjagiello-qa-homepage* has been rejected.",
            "attachments": [
                {
                    "color": "#f02b1d",
                    "fallback": "Deployment of kjagiello-qa-homepage has been rejected.",
                    "fields": [
                        {"title": "Pipeline", "value": "kjagiello-qa-homepage"},
                        {
                            "title": "Execution ID",
                            "value": (
                                "<https://eu-west-1.console.aws.amazon.com/"
                                "codesuite/codepipeline/pipelines/kjagiello-"
                                "qa-homepage/executions/0aeb1e48-4de1-4d3c-"
                                "8815-4a8a701b1fcc/timeline?region=eu-west-1|"
                                "0aeb1e48-4de1-4d3c-8815-4a8a701b1fcc>"
                            ),
                        },
                        {"title": "Environment", "value": "QA", "short": True},
                        {"title": "Region", "value": "eu-west-1", "short": True},
                        {
                            "title": "Code revision",
                            "value": (
                                "commit message\n\n"
                                "<http://foo.bar|View the changeset>"
                            ),
                        },
                    ],
                }
            ],
        },
    ),
]


@mock.patch.dict(os.environ, ENVIRONMENT)
class TestNotifier(unittest.TestCase):
    def test_send_notification_for_event(self):
        self.maxDiff = None
        for event, slack_message in TEST_MATRIX:
            with self.subTest(event):
                with mock.patch("urllib.request.urlopen") as urlopen_mock, mock.patch(
                    "notifier.get_codepipeline_client"
                ) as codepipeline_mock:
                    cm = mock.MagicMock()
                    cm.getcode.return_value = 200
                    cm.read.return_value = b"ok"
                    urlopen_mock.return_value = cm

                    codepipeline_mock.return_value = boto3.client("codepipeline")
                    with Stubber(codepipeline_mock.return_value) as stubber:
                        stubber.add_response(
                            "get_pipeline_execution", **PIPELINE_EXECUTION
                        )
                        notifier.handler(event=wrap_event(event), context={})

                    urlopen_mock.assert_called_once()
                    request = urlopen_mock.call_args[0][0]
                    self.assertEqual(request.full_url, ENVIRONMENT["SLACK_WEBHOOK_URL"])
                    self.assertEqual(
                        request.get_header("Content-type"), "application/json"
                    )
                    self.assertEqual(
                        json.loads(request.data),
                        slack_message,
                    )

    @mock.patch("urllib.request.urlopen")
    @mock.patch("notifier.get_codepipeline_client")
    def test_handles_missing_revision_gracefully(self, codepipeline_mock, urlopen_mock):
        # Get rid of the revision summary
        pipeline_execution = deepcopy(PIPELINE_EXECUTION)
        service_response = pipeline_execution["service_response"]
        del service_response["pipelineExecution"]["artifactRevisions"][0][
            "revisionSummary"
        ]

        codepipeline_mock.return_value = boto3.client("codepipeline")
        with Stubber(codepipeline_mock.return_value) as stubber:
            stubber.add_response("get_pipeline_execution", **pipeline_execution)
            notifier.handler(event=wrap_event(TEST_PIPELINE_UPDATE), context={})

        urlopen_mock.assert_called_once()
        request = urlopen_mock.call_args[0][0]
        payload = json.loads(request.data)
        revision_field = [
            field
            for field in payload["attachments"][0]["fields"]
            if field["title"] == "Code revision"
        ][0]
        self.assertEqual(revision_field["value"], "Unknown")


if __name__ == "__main__":
    unittest.main()
