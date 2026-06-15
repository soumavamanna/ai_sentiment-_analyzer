import asyncio

from infrastructure.scheduler.scheduler import (
    run
)

if __name__ == "__main__":

    asyncio.run(
        run()
    )