# -*- coding: utf-8 -*-
"""
Lacework Download File API wrapper.
"""

import json
import logging

logger = logging.getLogger(__name__)


class DownloadFileAPI(object):
    """
    Lacework Download File API.
    """

    def __init__(self, session):
        """
        Initializes the DownloadFileAPI object.

        :param session: An instance of the HttpSession class

        :return DownloadFileAPI object.
        """

        super(DownloadFileAPI, self).__init__()

        self._session = session

    def get(self, file=None):
        """
        A method to get the AWS CloudFormation template of the specified type.

        :param file: a string representing which template to download. ("aws-config" or "aws-cloudtrail")

        :return response json
        """

        # Build the Download File request URI
        api_uri = f"/api/v1/external/files/templates/{file}"

        response = self._session.get(api_uri)

        logger.debug(json.dumps(response.json(), indent=2))

        return response.json()