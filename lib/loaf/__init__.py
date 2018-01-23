import argparse
import asyncio
from pprint import pprint
import itertools
import json

import urwid

from loaf.slack_api import WebClient
from loaf.views import TeamOverview
from loaf import ui

loop = asyncio.get_event_loop()


def JSONType(value):
    with open(value, 'r') as fp:
        return json.load(fp)


async def run(config):
    overview = TeamOverview()

    for team in config.get('team', []):
        client = WebClient(team['token'], loop=loop)
        await overview.load_team(client)

    widget = ui.LoafWidget(overview)

    def send_message():
        coro = overview.send_message(widget.message.edit_text)

        if coro:
            loop.create_task(coro)

    urwid.connect_signal(widget.message, 'send', send_message)

    return widget


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--config', '-c',
        metavar='CONFIG',
        default='config.json',
        type=JSONType
    )
    args = parser.parse_args()

    loop = asyncio.get_event_loop()
    widget = loop.run_until_complete(run(args.config))

    urwid.MainLoop(widget, [
        ('selected', 'default, standout', 'default'),
        ('bold', 'default, bold', 'default')
    ], event_loop=urwid.AsyncioEventLoop(loop=loop)).run()


if __name__ == '__main__':
    main()
