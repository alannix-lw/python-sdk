# -*- coding: utf-8 -*-
"""
Test suite for the community-developed Python SDK for interacting with Lacework APIs.
"""
import calendar
import json
import time

from datetime import datetime

from laceworksdk.api.lql_queries import LQLQueriesAPI

end_time = calendar.timegm(time.gmtime())
start_time = end_time - 86400


def test_lql_queries_api_object_creation(api):
    assert isinstance(api.lql_queries, LQLQueriesAPI)


def test_lql_queries_api_env_object_creation(api_env):
    assert isinstance(api_env.lql_queries, LQLQueriesAPI)


def test_create(api, create_lql_query):
    unused_rand, unused_query_id, query_json, response = create_lql_query
    print(json.dumps(query_json, indent=4))

    assert 'data' in response


def test_compile(api, construct_lql_query):
    unused_rand, unused_query_id, query_json = construct_lql_query
    print(json.dumps(query_json, indent=4))

    response = api.lql_queries.compile(query_json)

    assert 'data' in response


def test_data_sources(api):
    response = api.lql_queries.data_sources()

    assert response['data']


def test_describe(api):
    response = api.lql_queries.describe('CloudTrailRawEvents')

    assert response['data']


def test_get(api):
    response = api.lql_queries.get()

    assert response['data']


def test_get_id(api, create_lql_query):
    unused_rand, query_id, unused_query_json, unused_response = create_lql_query

    response = api.lql_queries.get(query_id=query_id)

    assert len(response['data']) == 1


def test_run(api, construct_lql_query):
    unused_rand, unused_query_id, query_json = construct_lql_query
    print(json.dumps(query_json, indent=4))

    response = api.lql_queries.run(
        query_json,
        start_time_range=datetime.fromtimestamp(start_time).strftime('%Y-%m-%dT%H:%M:%SZ'),
        end_time_range=datetime.fromtimestamp(end_time).strftime('%Y-%m-%dT%H:%M:%SZ')
    )

    assert response['data']


def test_update(api, create_lql_query):
    unused_rand, query_id, query_json, unused_response = create_lql_query

    query_json['QUERY_TEXT'] = query_json['QUERY_TEXT'].replace('LIMIT 10', 'LIMIT 11')

    response = api.lql_queries.update(query_json)

    print(response)

    assert response['message']['lqlUpdated'] == query_id


def test_delete(api, create_lql_query):
    unused_rand, query_id, unused_query_json, unused_response = create_lql_query

    response = api.lql_queries.delete(query_id)

    assert response['message']['lqlDeleted'] == query_id
