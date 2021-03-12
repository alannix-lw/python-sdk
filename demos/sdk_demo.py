import argparse
import json
import os
import sys

from collections import namedtuple
from tabulate import tabulate

from laceworksdk import LaceworkClient, LaceworkContentRepository


class LaceworkPythonCLI(LaceworkClient):
    COMMAND = namedtuple(
        'Command',
        ['id', 'name_singular', 'name_plural', 'actions']
    )
    ACTION = namedtuple(
        'Action',
        ['id', 'name_verb', 'name_gerund', 'method']
    )

    def __init__(self, parsed_args=None):
        super().__init__()

        self.commands = [
            self.COMMAND(
                id='custom_policies',
                name_singular='Custom Policy',
                name_plural='Custom Policies',
                actions=[
                    self.ACTION(
                        id='create',
                        name_verb='Create',
                        name_gerund='Creating',
                        method=self.custom_policies.create
                    ),
                    self.ACTION(
                        id='delete',
                        name_verb='Delete',
                        name_gerund='Deleting',
                        method=self.custom_policies.delete
                    ),
                    self.ACTION(
                        id='disable',
                        name_verb='Disable',
                        name_gerund='Disabling',
                        method=self.custom_policies.disable
                    ),
                    self.ACTION(
                        id='enable',
                        name_verb='Enable',
                        name_gerund='Enabling',
                        method=self.custom_policies.enable
                    ),
                    self.ACTION(
                        id='find',
                        name_verb='Find',
                        name_gerund='Finding',
                        method=None
                    ),
                    self.ACTION(
                        id='get',
                        name_verb='Get',
                        name_gerund='Getting',
                        method=self.custom_policies.get
                    ),
                    self.ACTION(
                        id='update',
                        name_verb='Update',
                        name_gerund='Updating',
                        method=self.custom_policies.update
                    )
                ]
            ),
            self.COMMAND(
                id='lql_queries',
                name_singular='LQL Query',
                name_plural='LQL Queries',
                actions=[
                    self.ACTION(
                        id='create',
                        name_verb='Create',
                        name_gerund='Creating',
                        method=self.lql_queries.create
                    ),
                    self.ACTION(
                        id='compile',
                        name_verb='Compile',
                        name_gerund='Compiling',
                        method=self.lql_queries.compile
                    ),
                    self.ACTION(
                        id='data_sources',
                        name_verb='Data Sources',
                        name_gerund='Data Sourcing',
                        method=self.lql_queries.data_sources
                    ),
                    self.ACTION(
                        id='delete',
                        name_verb='Delete',
                        name_gerund='Deleting',
                        method=self.lql_queries.delete
                    ),
                    self.ACTION(
                        id='describe',
                        name_verb='Describe',
                        name_gerund='Describing',
                        method=self.lql_queries.describe
                    ),
                    self.ACTION(
                        id='get',
                        name_verb='Get',
                        name_gerund='Getting',
                        method=self.lql_queries.get
                    ),
                    self.ACTION(
                        id='run',
                        name_verb='Run',
                        name_gerund='Running',
                        method=self.lql_queries.run
                    ),
                    self.ACTION(
                        id='update',
                        name_verb='Update',
                        name_gerund='Updating',
                        method=self.lql_queries.update
                    )
                ]
            ),
            self.COMMAND(
                id='custom_reports',
                name_singular='Custom Report',
                name_plural='Custom Reports',
                actions=[]
            )
        ]
        self.parser = argparse.ArgumentParser(
            description='Lacework Python SDK'
        )
        self.command_subparsers = self.parser.add_subparsers(
            title='commands',
            description='Valid subcommands',
            dest='command',
            required=True
        )

        for command in self.commands:
            self.command_parser(command)

    def command_parser(self, command):
        _command_parser = self.command_subparsers.add_parser(
            command.id,
            help=f'Run and manage {command.name_plural}'
        )
        command_subparsers = _command_parser.add_subparsers(
            title='actions',
            description='Valid actions',
            dest='action',
            required=True
        )

        for action in command.actions:
            self.action_parser(command_subparsers, command, action)

    def action_parser(self, subparsers, command, action):
        _action_parser = subparsers.add_parser(
            action.id,
            help=f'{action.name_verb} {command.name_singular}',
        )

        # special handling for endpoints that don't need a "from"
        if action.id == 'data_sources':
            return
        elif action.id == 'describe':
            _action_parser.add_argument(
                'data_source',
                help=f'{command.name_singular} data source'
            )
            return
        elif action.id in ['delete', 'disable', 'enable', 'get']:
            _action_parser.add_argument(
                '--id' if action.id == 'get' else 'id',
                help=f'{command.name_singular} identifier'
            )
            if command.id == 'custom_policies' and action.id in ['enable', 'disable']:
                _action_parser.add_argument(
                    '--alert',
                    type=bool,
                    help='Whether optionally enable or disable alerting',
                    action=argparse.BooleanOptionalAction
                )
            return
        elif action.id == 'find':
            _action_parser.add_argument(
                'tag',
                help=f'{command.name_singular} tag'
            )
            return

        action_subparsers = _action_parser.add_subparsers(
            title='From',
            description='Valid Sources',
            dest='from_where',
            required=True
        )

        from_wheres = {
            'from_file': f'{action.name_verb} {command.name_singular} from Local File',
            'from_repo': f'{action.name_verb} {command.name_singular} from Active Repository',
            'from_url': f'{action.name_verb} {command.name_singular} from URL'
        }
        if action.id in ['compile', 'run']:
            from_wheres['from_env'] = f'{action.name_verb} {command.name_singular} from Lacework environment'

        for from_where, help_text in from_wheres.items():
            self.from_where_parser(
                action_subparsers, from_where, help_text, command, action)

    def from_where_parser(
            self, subparsers, from_where, help_text, command, action):
        _from_where_parser = subparsers.add_parser(
            from_where,
            help=help_text
        )

        if from_where == 'from_file':
            _from_where_parser.add_argument(
                'uri',
                metavar='file_path',
                help=f'{command.name_singular} file path'
            )
        elif from_where in ['from_repo', 'from_env']:
            _from_where_parser.add_argument(
                'uri',
                metavar='id',
                help=f'{command.name_singular} identifier'
            )
        elif from_where == 'from_url':
            _from_where_parser.add_argument(
                'uri',
                metavar='url',
                help=f'{command.name_singular} URL'
            )

        # special handling for endpoints that need additional arguments (i.e. run)
        if action.id in ['run']:
            _from_where_parser.add_argument(
                '--start',
                help=f'{command.name_singular} start time'
            )
            _from_where_parser.add_argument(
                '--end',
                help=f'{command.name_singular} end time'
            )


if __name__ == '__main__':
    lw_cli = LaceworkPythonCLI()
    args = lw_cli.parser.parse_args()

    lw_client = LaceworkClient()
    lw_content = LaceworkContentRepository(
        config_file_path='./lacework.conf'
    )
    # index = lw_content.index

    command = [x for x in lw_cli.commands if x.id == args.command][0]
    action = [x for x in command.actions if x.id == args.action][0]

    if command.id == 'lql_queries':
        try:
            from_where = args.from_where
        except AttributeError:
            from_where = None

        if action.id == 'data_sources':
            response = lw_client.lql_queries.data_sources()

        elif action.id == 'describe':
            response = lw_client.lql_queries.describe(args.data_source)

        elif action.id == 'get':
            try:
                query_id = args.id
            except AttributeError:
                query_id = None

            response = lw_client.lql_queries.get(query_id=query_id)

        elif args.from_where == 'from_env':
            try:
                start_time_range = args.start
            except AttributeError:
                start_time_range = None
            try:
                end_time_range = args.end
            except AttributeError:
                end_time_range = None

            print(f'Acquiring {command.name_singular}: {args.uri}\n')
            response = lw_client.lql_queries.get(args.uri)
            query_json = response['data'][0]
            query_text = response['data'][0]['query_text']

            print(query_text)
            print('\n')

            print(f'{action.name_gerund} {command.name_singular}: {args.uri}\n')

            if action.id == 'compile':
                response = lw_client.lql_queries.compile(query_json)

            elif action.id == 'run':
                response = lw_client.lql_queries.run(
                    query_json,
                    start_time_range=start_time_range,
                    end_time_range=end_time_range
                )
            else:
                raise NotImplementedError

        elif args.from_where == 'from_file':
            file_path = os.path.realpath(args.uri)
            assert os.path.isfile(args.uri)

            file_name = os.path.basename(file_path)
            assert file_name.endswith('.json')

            print(f'Reading {file_name}')
            with open(file_path, mode='r', newline='') as fh:
                query_json = json.loads(fh.read())

            print(f'{action.name_gerund} {command.name_singular}: {file_name}\n')
            response = lw_client.lql_queries.create(query_json)

        elif args.from_where == 'from_repo':
            print(f'Acquiring {command.name_singular}: {args.uri}\n')
            query = lw_content.get_query(args.uri)
            print(query.raw)

            if action.id == 'compile':
                print(f'{action.name_gerund} {command.name_singular}: {args.uri}\n')
                response = lw_client.lql_queries.compile(query.json)
            elif action.id == 'create':
                print(f'{action.name_gerund} {command.name_singular}: {args.uri}\n')
                response = lw_client.lql_queries.create(query.json, smart=True)
            elif action.id == 'run':
                try:
                    start_time_range = args.start
                except AttributeError:
                    start_time_range = None
                try:
                    end_time_range = args.end
                except AttributeError:
                    end_time_range = None

                print(f'{action.name_gerund} {command.name_singular}: {args.uri}\n')
                response = lw_client.lql_queries.run(
                    query.json, start_time_range=start_time_range, end_time_range=end_time_range)
            else:
                raise NotImplementedError

        else:
            raise NotImplementedError

    elif command.id == 'custom_policies':
        if action.id == 'create':
            if args.from_where == 'from_file':
                file_path = os.path.realpath(args.uri)
                assert os.path.isfile(args.uri)

                file_name = os.path.basename(file_path)
                assert file_name.endswith('.json')

                print(f'Reading {file_name}')

                with open(file_path, mode='r', newline='') as fh:
                    policy_json = json.loads(fh.read())

                print(f'{action.name_gerund} {command.name_singular}: {file_name}\n')
                response = lw_client.custom_policies.create(policy_json)
            elif args.from_where == 'from_repo':
                print(f'Acquiring {command.name_singular}: {args.uri}\n')

                policy, query = lw_content.get_policy(args.uri)

                print(json.dumps(policy.json, indent=4))
                print('\n')
                print(query.raw)
                print('\n')

                print(f'{action.name_gerund} LQL Query: {query.id}\n')
                response = lw_client.lql_queries.create(query.json, smart=True)
                print(json.dumps(response, indent=4))
                print('\n')

                print(f'{action.name_gerund} {command.name_singular}: {args.uri}\n')
                response = lw_client.custom_policies.create(policy.json)
            else:
                raise NotImplementedError
        elif action.id == 'delete':
            response = lw_client.custom_policies.delete(policy_id=args.id)
        elif action.id == 'find':
            policies = lw_content.find_policies(args.tag)
            print(tabulate(policies, headers='keys'))
            sys.exit(0)
        elif action.id == 'get':
            try:
                policy_id = args.id
            except AttributeError:
                policy_id = None

            response = lw_client.custom_policies.get(policy_id=policy_id)
        else:
            raise NotImplementedError

    else:
        raise NotImplementedError

    print(json.dumps(response, indent=4))
