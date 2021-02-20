# -*- coding: utf-8 -*-
"""
Test suite for the community-developed Python SDK for interacting with Lacework APIs.
"""

import random
import string

from laceworksdk.api.report_rules import ReportRulesAPI

ALERT_RULE_GUID = None
RANDOM_TEXT = "".join(random.choice(string.ascii_uppercase + string.digits) for _ in range(8))


# Tests

def test_report_rules_api_object_creation(api):
    assert isinstance(api.report_rules, ReportRulesAPI)


def test_report_rules_api_env_object_creation(api_env):
    assert isinstance(api_env.report_rules, ReportRulesAPI)


def test_report_rules_api_get(api):
    response = api.report_rules.get()
    assert "data" in response.keys()


def test_report_rules_api_get_by_guid(api):
    response = api.report_rules.get()

    if len(response) > 0:
        report_rule_guid = random.choice(response["data"])["mcGuid"]

        response = api.report_rules.get_by_guid(guid=report_rule_guid)

        assert "data" in response.keys()
        assert response["data"]["mcGuid"] == report_rule_guid


def test_report_rules_api_create(api):

    response = api.alert_channels.search(
        query_data={
            "filters": [
                {
                    "expression": "eq",
                    "field": "type",
                    "value": "EmailUser"
                }
            ],
            "returns": [
                "intgGuid"
            ]
        }
    )
    alert_channel_guid = random.choice(response["data"])["intgGuid"]

    response = api.resource_groups.search(
        query_data={
            "filters": [
                {
                    "expression": "eq",
                    "field": "resourceType",
                    "value": "AWS"
                }
            ],
            "returns": [
                "resourceGuid"
            ]
        }
    )
    resource_group_guid = random.choice(response["data"])["resourceGuid"]

    response = api.report_rules.create(
        type="Report",
        filters={
            "name": f"Test Report Rule {RANDOM_TEXT}",
            "description": f"Test Report Rule Description {RANDOM_TEXT}",
            "enabled": 1,
            "resourceGroups": [resource_group_guid],
            "severity": [1, 2, 3]
        },
        intg_guid_list=[alert_channel_guid],
        report_notification_types={
            "awsComplianceEvents": True,
            "awsCisS3": True
        }
    )

    assert "data" in response.keys()

    global REPORT_RULE_GUID
    REPORT_RULE_GUID = response["data"]["mcGuid"]


def test_report_rules_api_search(api):
    response = api.report_rules.search(query_data={
        "filters": [
            {
                "expression": "eq",
                "field": "type",
                "value": "Report"
            }
        ],
        "returns": [
            "mcGuid"
        ]
    })
    assert "data" in response.keys()


def test_report_rules_api_update(api):
    if REPORT_RULE_GUID:
        response = api.report_rules.update(
            REPORT_RULE_GUID,
            filters={
                "name": f"Test Report Rule {RANDOM_TEXT} (Updated)",
                "enabled": False
            }
        )

        assert "data" in response.keys()

    assert REPORT_RULE_GUID is not None


def test_report_rules_api_delete(api):
    if REPORT_RULE_GUID:
        response = api.report_rules.delete(REPORT_RULE_GUID)
        assert response.status_code == 204

    assert REPORT_RULE_GUID is not None
