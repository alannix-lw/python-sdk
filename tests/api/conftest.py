# -*- coding: utf-8 -*-
"""
Test suite for the community-developed Python SDK for interacting with Lacework APIs.
"""
import pytest
import random


BASE_LQL_QUERY = (
    '{query_id}(CloudTrailRawEvents e) {{\n'
    '    SELECT INSERT_ID\n'
    '    LIMIT 10\n'
    '}}'
)


@pytest.fixture(scope='module')
def construct_lql_query():
    rand = random.randint(0, 1000000)
    query_id = f'MyLQL{rand}'
    query_json = {
        'QUERY_TEXT': BASE_LQL_QUERY.format(query_id=query_id)
    }

    yield rand, query_id, query_json


@pytest.fixture(scope='module')
def create_lql_query(api, construct_lql_query):
    rand, query_id, query_json = construct_lql_query

    response = api.lql_queries.create(query_json)

    yield rand, query_id, query_json, response

    try:
        api.lql_queries.delete(query_id)
    except Exception:
        pass
