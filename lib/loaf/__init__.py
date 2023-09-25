import argparse
import asyncio
from pprint import pprint
from xdg.BaseDirectory import xdg_config_home
import itertools
import json
import operator
import os

import urwid

from loaf.slack_api import WebClient
from loaf.models import TeamOverview, Team, User
from loaf import ui

loop = asyncio.get_event_loop()


def JSONType(value):
    with open(value, 'r') as fp:
        return json.load(fp)


async def run(config):
    overview = TeamOverview()
    widget = ui.LoafWidget(overview)

    for team_config in config.get('team', []):
        client = WebClient(team_config['token'], loop=loop)

        rtm_client, team_info = await asyncio.gather(
            client.rtm.connect(),
            client.auth.test()
        )
        getter = operator.itemgetter('user_id', 'user', 'team_id', 'team')
        user_id, user, team_id, team = getter(team_info)

        team = Team(
            team_id, team, User(user_id, user),
            web_api=client, rtm_api=rtm_client,
            alias=team_config.get('alias', None),
            duration=int(team_config.get('history_weeks', 1)),
            sync_dir=team_config.get('sync_dir', None)
        )
        await asyncio.gather(team.load_converstions(), team.load_users())

        rtm_client.on('message', team.handle_message)

        overview.add_team(team)

    return widget


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--config', '-c',
        metavar='CONFIG',
        default=os.path.join(xdg_config_home, 'loaf', 'config.json'),
        type=JSONType
    )
    args = parser.parse_args()

    loop = asyncio.get_event_loop()
    widget = loop.run_until_complete(run(args.config))

    widget.main_loop = urwid.MainLoop(widget, [
        ('selected', 'default, standout', 'default'),
        ('username', 'default, bold', 'default'),
        ('timestamp', 'default, underline', 'default')
    ], event_loop=urwid.AsyncioEventLoop(loop=loop))
    widget.main_loop.run()


if __name__ == '__main__':
    main()
