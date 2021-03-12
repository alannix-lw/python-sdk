# -*- coding: utf-8 -*-
import logging

from urllib.parse import quote

from laceworksdk.exceptions import ApiError

logger = logging.getLogger(__name__)


class LQLQueriesAPI(object):
    """
    Lacework LQL Query API.
    """

    def __init__(self, session):
        """
        Initializes the LQLQueriesAPI object.

        Parameters:
        session (HttpSession): An instance of the HttpSession class.

        Returns:
        LQLQueriesAPI object
        """
        super(LQLQueriesAPI, self).__init__()

        self.lql_queries_base_uri = '/api/v1/external/lql'
        self.lql_queries_identifier_key = 'LQL_ID'
        self._session = session

    def create(self, query_json, smart=False):
        """
        Create an LQL Query

        Parameters:
        query_json (dict): LQL Query JSON
        smart (bool): Whether to update if query already exists

        Return:
        response (dict): requests json() object
        """
        api_uri = self.lql_queries_base_uri

        try:
            response = self._session.post(api_uri, data=query_json)
        except ApiError as e:
            if smart and 'already exists' in str(e):
                return self.update(query_json)
            raise

        return response.json()

    def compile(self, query_json):
        """
        Compile an LQL Query

        Parameters:
        query_json (dict): LQL Query JSON

        Return:
        response (dict): requests json() object
        """
        api_uri = f'{self.lql_queries_base_uri}/compile'

        response = self._session.post(api_uri, data=query_json)

        return response.json()

    def data_sources(self):
        """
        Get LQL Data Sources

        Return:
        response (dict): requests json() object
        """
        api_uri = f'{self.lql_queries_base_uri}/dataSources'

        response = self._session.get(api_uri)

        return response.json()

    def delete(self, query_id):
        """
        Delete an LQL Query

        Parameters:
        query_id (str): LQL Query ID

        Return:
        response (dict): requests json() object
        """
        api_uri = (
            f'{self.lql_queries_base_uri}'
            f'?{self.lql_queries_identifier_key}={quote(query_id, safe="")}'
        )

        response = self._session.delete(api_uri)

        return response.json()

    def describe(self, data_source):
        """
        Describe an LQL Data Source

        Parameters:
        data_source (str): LQL Data Source

        Return:
        response (dict): requests json() object
        """
        api_uri = f'{self.lql_queries_base_uri}/describe/{quote(data_source, safe="")}'

        response = self._session.get(api_uri)

        return response.json()

    def get(self, query_id=None):
        """
        Get an LQL Query or Queries

        If called without query_id return all queries.
        Otherwise return specified query.

        Parameters:
        query_id (str): LQL Query ID (optional)

        Return:
        response (dict): requests json() object
        """
        api_uri = self.lql_queries_base_uri

        if query_id:
            api_uri += f'?{self.lql_queries_identifier_key}={quote(query_id, safe="")}'

        response = self._session.get(api_uri)

        return response.json()

    def run(self, query_json, start_time_range=None, end_time_range=None):
        """
        Run an LQL Query

        Start and End time ranges are required to run LQL Queries.

        start_time_range and end_time_range parameters are optional
        unless they are not specified in the query_json

        Parameters:
        query_json (dict): LQL Query JSON
        start_time_range (str): The start time range of the query
        end_time_range (str): The end time range of the query

        Return:
        response (dict): requests json() object
        """
        api_uri = f'{self.lql_queries_base_uri}/query'

        if isinstance(start_time_range, (int, str)) and str(start_time_range):
            query_json['START_TIME_RANGE'] = start_time_range
            try:
                del query_json['StartTimeRange']
            except Exception:
                pass
        if isinstance(end_time_range, (int, str)) and str(end_time_range):
            query_json['END_TIME_RANGE'] = end_time_range
            try:
                del query_json['EndTimeRange']
            except Exception:
                pass

        assert 'StartTimeRange' in query_json or 'START_TIME_RANGE' in query_json,\
            'Query must specify a valid StartTimeRange'
        assert 'EndTimeRange' in query_json or 'END_TIME_RANGE' in query_json,\
            'Query must specify a valid EndTimeRange'

        response = self._session.post(api_uri, data=query_json)

        return response.json()

    def update(self, query_json):
        """
        Update an LQL Query

        Parameters:
        query_json (dict): LQL Query JSON

        Return:
        response (dict): requests json() object
        """
        api_uri = self.lql_queries_base_uri

        response = self._session.patch(api_uri, data=query_json)

        return response.json()
