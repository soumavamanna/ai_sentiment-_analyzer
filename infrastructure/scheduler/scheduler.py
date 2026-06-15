import asyncio

from ingestion.news.news_service import (
    get_relevant_news
)

from ingestion.market.market_collector import (
    fetch_market_data
)

async def run():

    while True:

        news = await (
            get_relevant_news()
        )

        print(
            f"Relevant News: {len(news)}"
        )

        market = (
            fetch_market_data()
        )

        print(
            f"Market Rows: {len(market)}"
        )

        await asyncio.sleep(
            900
        )