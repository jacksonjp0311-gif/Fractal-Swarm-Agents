from __future__ import annotations

import asyncio
from contextlib import asynccontextmanager


class Scheduler:
    """
    Async concurrency gate (global).
    """

    def __init__(self, max_concurrency: int) -> None:
        self._sem = asyncio.Semaphore(max(1, int(max_concurrency)))

    @asynccontextmanager
    async def slot(self):
        await self._sem.acquire()
        try:
            yield
        finally:
            self._sem.release()