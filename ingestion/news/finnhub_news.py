import aiohttp
import asyncio
import os
from dotenv import load_dotenv
from infrastructure.cache.redis_client import (
    redis_client
)

from infrastructure.rate_limit.limiter import (
    RateLimiter
)

limiter = RateLimiter(
    max_calls=30,
    period=60
)
load_dotenv()
FINNHUB_KEY = os.getenv("FINNHUB_KEY")

async def fetch_news():

    await limiter.wait()

    last_ts = redis_client.get(
        "finnhub_last_ts"
    )

    url = (
        "https://finnhub.io/api/v1/news"
        "?category=general"
        f"&token={FINNHUB_KEY}"
    )

    async with aiohttp.ClientSession() as session:

        async with session.get(url) as r:

            news = await r.json()
    fresh = []

    newest_ts = last_ts

    for article in news:

        ts = article["datetime"]

        if (
            last_ts and
            ts <= int(last_ts)
        ):
            continue

        fresh.append(article)

        if (
            newest_ts is None
            or
            ts > int(newest_ts)
        ):
            newest_ts = ts

    if newest_ts:
        redis_client.set(
            "finnhub_last_ts",
            newest_ts
        )

    return fresh