import asyncio
import time

class RateLimiter:

    def __init__(
        self,
        max_calls,
        period
    ):
        self.max_calls = max_calls
        self.period = period

        self.calls = []

    async def wait(self):

        now = time.time()

        self.calls = [
            call
            for call in self.calls
            if now - call < self.period
        ]

        if (
            len(self.calls)
            >= self.max_calls
        ):

            wait_time = (
                self.period -
                (now - self.calls[0])
            )

            await asyncio.sleep(
                wait_time
            )

        self.calls.append(
            time.time()
        )