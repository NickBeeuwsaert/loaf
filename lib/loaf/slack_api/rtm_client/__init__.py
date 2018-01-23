import asyncio
import itertools
from collections import defaultdict

from ...event_emitter import EventEmitter

_counter = itertools.count(1)


class RTMError(Exception):
    pass


class RTMClient(EventEmitter):
    def __init__(self, ws, *, loop=None):
        if loop is None:
            loop = asyncio.get_event_loop()

        self.loop = loop
        self.ws = ws
        self._futures = {}

        loop.create_task(self._recv_loop())

    async def _recv_loop(self):
        while True:
            message = await self.ws.receive_json()

            try:
                future = self._futures.pop(message['reply_to'])
            except KeyError:
                self.emit(message['type'], message)
            else:
                if message['ok'] is False:
                    future.set_exception(RTMError(message['error']))
                else:
                    future.set_result(message)

    async def send(self, message):
        id = next(_counter)

        future = self.loop.create_future()
        self._futures[id] = future
        await self.ws.send_json(dict(
            id=id,
            **message
        ))
        return await future
