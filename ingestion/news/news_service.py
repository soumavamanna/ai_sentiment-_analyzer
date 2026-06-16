from ingestion.news.rss_news import fetch_news
from services.filtering_service import article_relevant

async def get_relevant_news():
    # Gather free data streams concurrently
    news = await fetch_news()
    print(f"Fetched {len(news)} raw articles from Indian RSS feeds.")
    
    # Run filtering over text matches against your target tickers
    filtered = [
        article
        for article in news
        if article_relevant(article)
    ]
    
    print(f"Filtered down to {len(filtered)} relevant articles matching your Universe.")
    return filtered