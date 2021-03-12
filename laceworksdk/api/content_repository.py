# -*- coding: utf-8 -*-
import json
import logging
import os
import re
import requests

from collections import namedtuple
from github import Github

from laceworksdk.config import parse_conf_file

logger = logging.getLogger(__name__)


class ContentRepository():
    """
    ContentRepository API

    This class loads Lacework Content Repositories to
    facilitate "remote" acquisition of content resources.

    Repositories can be loaded from a lacework.conf file or a
    single repository can be passed during class instantiation.
    """

    REPO_STANZA_RE = re.compile('^(?:(?:content_repository)|content_repository:(.+))$')
    DEFAULT_REPO_ID = '_default'
    DEFAULT_REPO_TYPE = 'github'
    DEFAULT_REPO_REF = 'main'

    POLICY = namedtuple('Policy', ['id', 'uri', 'json', 'raw'])
    QUERY = namedtuple('Query', ['id', 'uri', 'json', 'raw'])

    def __init__(
            self,
            config_file_path=None,
            typ=None,
            uri=None,
            ref=None,
            token=None):
        """"
        Initializes the ContentRepository object.

        Parameters:
        config_file_path (str): File path to content repository configurations (i.e. lacework.conf)
        typ (str): Repository type if not specifying a config_file_path
        uri (str): Repository uri if not specifying a config_file_path
        token (str): Repository token if not specifying a config_file_path
        ref (str): Repository reference if not specifying a config_file_path

        Returns:
        ContentRepository object
        """
        # {
        #     '<repo_id>': {
        #         'type': 'local|github',
        #         'uri': '<uri>',
        #         'token': '<token>',
        #         'ref': '<ref>'
        #     }
        # }
        self.config_file_path = None
        self.repos = {}
        self.active_repo_id = None

        # 1. If configuration file exists, load it
        if isinstance(config_file_path, str) and os.path.isfile(config_file_path):
            self.config_file_path = os.path.realpath(config_file_path)
            self.load_config(config_file_path)

        # 2. Single instance mode
        elif uri and isinstance(uri, str):
            self.repos[self.DEFAULT_REPO_ID] = {
                'type': typ or self.DEFAULT_REPO_TYPE,
                'uri': uri,
                'token': token,
                'ref': ref or self.DEFAULT_REPO_REF,
            }
            self.active_repo_id = self.DEFAULT_REPO_ID

        assert self.repos, 'No content repositories found!'

        self.load_index()

    def load_config(self, config_file_path):
        """
        Loads config_items from config_file_path
        to self.repos and self.active_repo_id

        Parameters:
        config_file_path (str): File path to content repository configurations (i.e. lacework.conf)

        Sample lacework.conf:
        [content_repository]
        active_repository = hazedav-private

        [content_repository:hazedav-private]
        type = github
        uri = hazedav/lacework-dev
        ref = main
        token = ****************************************
        """
        config_items = parse_conf_file(self.config_file_path)

        for stanza, settings in config_items.items():
            stanza_match = self.REPO_STANZA_RE.match(stanza)

            if not stanza_match:
                continue

            try:
                repo_id = stanza_match.group(1)
                if not repo_id:
                    raise IndexError

                self.repos[repo_id] = {
                    'type': settings.get('type') or self.DEFAULT_REPO_TYPE,
                    'uri': settings.get('uri'),
                    'ref': settings.get('ref') or self.DEFAULT_REPO_REF,
                    'token': settings.get('token')
                }
            except IndexError:
                self.active_repo_id = settings.get('active_repository')

            if (self.repos
                    and self.active_repo_id
                    and self.active_repo_id in self.repos):
                return
            elif self.repos:
                # activate the first repository
                self.active_repo_id = list(self.repos)[0]

    def load_index(self):
        """
        Load content.index from active repository
        """
        content_repo = self.repos[self.active_repo_id]

        if content_repo['type'] == 'github':
            content_file = ContentRepository.get_index_from_github(content_repo)
            self.index = json.loads(content_file.decoded_content.decode('utf-8'))
        else:
            raise NotImplementedError

    @staticmethod
    def get_index_from_github(content_repo):
        """
        Retrieve content.index from Lacework Content Repository backed by Github

        Parameters:
        content_repo (dict): A self.repos{} dictionary item

        Returns:
        content_file (Github.ContentFile): content.index ContentFile
        """
        github_repo = Github(content_repo['token']).get_repo(content_repo['uri'])
        return github_repo.get_contents('content.index', ref=content_repo['ref'])

    def find_policies(self, tag):
        """
        Find policies based on tags from the current index

        Parameters:
        tag (str): A policy tag value

        Returns:
        policies (list of dicts): A list of policy dictionaries
        [
            {
                'policy_id': <policy id>,
                'title': <policy title>,
                'description': <policy description>
            }
        ]
        """
        policy_ids = self.index.get('policy_tags', {}).get(tag, [])
        return [
            {
                'policy_id': policy_id,
                'title': self.index['policies'][policy_id]['title'],
                'description': self.index['policies'][policy_id]['description'],
            }
            for policy_id in policy_ids
        ]

    def get_policy(self, policy_id):
        """
        Get policy references based on policy_id

        Parameters:
        policy_id (str): A policy identifier

        Returns:
        policy, query (POLICY namedtuple, QUERY namedtuple): policy and query namedtuples
        """
        if self.repos[self.active_repo_id]['type'] == 'github':
            references = self.index['policies'][policy_id]['references']

            for reference in references:
                uri = reference['uri']

                headers = {
                    'Accept': 'application/vnd.github.v3.raw',
                }
                if 'token' in self.repos[self.active_repo_id]:
                    headers['Authorization'] = f'token {self.repos[self.active_repo_id]["token"]}'

                r = requests.get(
                    uri,
                    headers=headers
                )
                # raise for 400/500
                r.raise_for_status()

                # load github blob using json and lower case all keys
                r_data = {k.lower(): v for k, v in json.loads(r.text).items()}

                if reference['content_type'] == 'query':
                    query = self.QUERY(
                        id=reference['id'],
                        uri=reference['uri'],
                        json=r_data,
                        raw=r_data['query_text']
                    )
                elif reference['content_type'] == 'policy':
                    policy = self.POLICY(
                        id=reference['id'],
                        uri=reference['uri'],
                        json=r_data,
                        raw=r_data
                    )
            return policy, query
        else:
            raise NotImplementedError

    def get_query(self, query_id):
        """
        Get query reference based on query_id

        Parameters:
        query_id (str): A query identifier

        Returns:
        query (QUERY namedtuple): query namedtuple
        """
        if self.repos[self.active_repo_id]['type'] == 'github':
            reference = self.index['queries'][query_id]['references'][0]
            uri = reference['uri']

            headers = {
                'Accept': 'application/vnd.github.v3.raw',
            }
            if 'token' in self.repos[self.active_repo_id]:
                headers['Authorization'] = f'token {self.repos[self.active_repo_id]["token"]}'

            r = requests.get(
                uri,
                headers=headers
            )
            # raise for 400/500
            r.raise_for_status()

            # load github blob using json and lower case all keys
            query_data = {k.lower(): v for k, v in json.loads(r.text).items()}

            return self.QUERY(
                id=query_id,
                uri=uri,
                json=query_data,
                raw=query_data['query_text']
            )
        else:
            raise NotImplementedError

    def get_report(self, report_id):
        raise NotImplementedError
