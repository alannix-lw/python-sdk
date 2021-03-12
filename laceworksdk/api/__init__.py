# -*- coding: utf-8 -*-
"""
Lacework API wrappers.
"""

import os

from dotenv import load_dotenv
from laceworksdk.http_session import HttpSession
from .agent_access_tokens import AgentAccessTokensAPI
from .alert_channels import AlertChannelsAPI
from .alert_rules import AlertRulesAPI
from .audit_logs import AuditLogsAPI
from .cloudtrail import CloudTrailAPI
from .compliance import ComplianceAPI
from .content_repository import ContentRepository
from .contract_info import ContractInfoAPI
from .custom_compliance_config import CustomComplianceConfigAPI
from .download_file import DownloadFileAPI
from .events import EventsAPI
from .integrations import IntegrationsAPI
from .custom_policies import CustomPoliciesAPI
from .lql_queries import LQLQueriesAPI
from .report_rules import ReportRulesAPI
from .resource_groups import ResourceGroupsAPI
from .run_reports import RunReportsAPI
from .schemas import SchemasAPI
from .team_members import TeamMembersAPI
from .token import TokenAPI
from .vulnerability import VulnerabilityAPI

from laceworksdk.config import (
    LACEWORK_ACCOUNT_ENVIRONMENT_VARIABLE,
    LACEWORK_SUBACCOUNT_ENVIRONMENT_VARIABLE,
    LACEWORK_API_KEY_ENVIRONMENT_VARIABLE,
    LACEWORK_API_SECRET_ENVIRONMENT_VARIABLE,
    LACEWORK_API_BASE_DOMAIN_ENVIRONMENT_VARIABLE
)

load_dotenv()


class LaceworkClient(object):
    """
    Lacework API wrapper for Python.
    """

    def __init__(self,
                 account=None,
                 subaccount=None,
                 api_key=None,
                 api_secret=None,
                 instance=None,
                 base_domain=None):
        """
        Initializes the Lacework Client object.

        :return LaceworkClient object.
        """

        # Attempt to use Environment Variables
        self._account = account or instance or os.getenv(LACEWORK_ACCOUNT_ENVIRONMENT_VARIABLE)
        self._subaccount = subaccount or os.getenv(LACEWORK_SUBACCOUNT_ENVIRONMENT_VARIABLE)
        self._api_key = api_key or os.getenv(LACEWORK_API_KEY_ENVIRONMENT_VARIABLE)
        self._api_secret = api_secret or os.getenv(LACEWORK_API_SECRET_ENVIRONMENT_VARIABLE)
        self._base_domain = base_domain or os.getenv(LACEWORK_API_BASE_DOMAIN_ENVIRONMENT_VARIABLE)

        # Create an HttpSession instance
        self._session = HttpSession(
            self._account,
            self._subaccount,
            self._api_key,
            self._api_secret,
            self._base_domain
        )

        # API Wrappers
        self.agent_access_tokens = AgentAccessTokensAPI(self._session)
        self.alert_channels = AlertChannelsAPI(self._session)
        self.alert_rules = AlertRulesAPI(self._session)
        self.audit_logs = AuditLogsAPI(self._session)
        self.cloudtrail = CloudTrailAPI(self._session)
        self.compliance = ComplianceAPI(self._session)
        self.compliance.config = CustomComplianceConfigAPI(self._session)
        self.contract_info = ContractInfoAPI(self._session)
        self.events = EventsAPI(self._session)
        self.files = DownloadFileAPI(self._session)
        self.custom_policies = CustomPoliciesAPI(self._session)
        self.lql_queries = LQLQueriesAPI(self._session)
        self.integrations = IntegrationsAPI(self._session)
        self.report_rules = ReportRulesAPI(self._session)
        self.resource_groups = ResourceGroupsAPI(self._session)
        self.run_reports = RunReportsAPI(self._session)
        self.schemas = SchemasAPI(self._session)
        self.team_members = TeamMembersAPI(self._session)
        self.tokens = TokenAPI(self._session)
        self.vulnerabilities = VulnerabilityAPI(self._session)


class LaceworkContentRepository(ContentRepository):

    def __init__(self, config_file_path=None, typ=None, uri=None, ref=None, token=None):
        super().__init__(config_file_path, typ, uri, ref, token)
