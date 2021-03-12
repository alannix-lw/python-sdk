# -*- coding: utf-8 -*-
"""
Test suite for the community-developed Python SDK for interacting with Lacework APIs.
"""

pytest_plugins = [
    "tests.test_laceworksdk",
    "tests.api",
    "tests.api.test_agent_access_tokens",
    "tests.api.test_alert_channels",
    "tests.api.test_alert_rules",
    "tests.api.test_audit_logs",
    "tests.api.test_cloudtrail",
    "tests.api.test_compliance",
    "tests.api.test_contract_info",
    "tests.api.test_custom_compliance_config",
    "tests.api.test_custom_policies",
    "tests.api.test_download_file",
    "tests.api.test_events",
    "tests.api.test_integrations",
    "tests.api.test_lql_queries",
    "tests.api.test_report_rules",
    "tests.api.test_resource_groups",
    "tests.api.test_run_reports",
    "tests.api.test_schemas",
    "tests.api.test_team_members",
    "tests.api.test_token",
    "tests.api.test_vulnerability",
]
