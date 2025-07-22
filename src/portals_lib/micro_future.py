import asyncio


class MicroFuture:
    def __init__(self):
        self._event = asyncio.Event()
        self._result = None
        self._exception = None
        self._done = False

    def set_result(self, result):
        self._result = result
        self._done = True
        self._event.set()

    def set_exception(self, exception):
        self._exception = exception
        self._done = True
        self._event.set()

    async def wait(self):
        await self._event.wait()
        if self._exception:
            raise self._exception
        return self._result

    def done(self):
        return self._done
