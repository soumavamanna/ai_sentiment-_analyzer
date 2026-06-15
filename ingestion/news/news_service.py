from ingestion.news.finnhub_news import (
    fetch_news
)

from services.filtering_service import (
    article_relevant
)

async def get_relevant_news():

    news = await fetch_news()

    filtered = [
        article
        for article in news
        if article_relevant(article)
    ]

    return filtered