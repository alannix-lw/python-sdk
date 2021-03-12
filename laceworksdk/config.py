# -*- coding: utf-8 -*-
"""
Package configuration.
"""
import re

from configparser import RawConfigParser

# Package Constants
DEFAULT_BASE_DOMAIN = "lacework.net"
DEFAULT_ACCESS_TOKEN_EXPIRATION = 3600
DEFAULT_SUCCESS_RESPONSE_CODES = [200, 201, 204]

# Environment Variable Definitions
LACEWORK_ACCOUNT_ENVIRONMENT_VARIABLE = "LW_ACCOUNT"
LACEWORK_SUBACCOUNT_ENVIRONMENT_VARIABLE = "LW_SUBACCOUNT"
LACEWORK_API_KEY_ENVIRONMENT_VARIABLE = "LW_API_KEY"
LACEWORK_API_SECRET_ENVIRONMENT_VARIABLE = "LW_API_SECRET"
LACEWORK_API_BASE_DOMAIN_ENVIRONMENT_VARIABLE = "LW_BASE_DOMAIN"


def parse_conf_file(file_path):
    with open(file_path, 'r', encoding='utf-8-sig', newline=None) as fh:
        file_data = fh.read()

    config = RawConfigParser(
        allow_no_value=False,
        strict=True
    )
    # preserve case
    config.optionxform = str
    # RFC822: replace escaped newlines
    file_data.replace('\\\n', '\n\t')
    # replace whitespace preceding comments
    file_data = re.sub(r'^\s+#', '#', file_data, flags=re.MULTILINE)

    config.read_string(file_data)

    return {x: dict(config.items(x)) for x in config.sections()}
