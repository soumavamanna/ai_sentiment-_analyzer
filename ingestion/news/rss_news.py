import aiohttp
import asyncio
import feedparser
import time
from datetime import datetime, timezone
from infrastructure.cache.redis_client import redis_client
from utils.cache_manager import CacheManager
# A dictionary of top-tier Indian financial RSS feeds
RSS_FEEDS = {
    "Economic Times Markets": "https://economictimes.indiatimes.com/markets/rssfeeds/1977021501.cms",
    "Moneycontrol Top News": "https://www.moneycontrol.com/rss/MCtopnews.xml",
    "Livemint Markets": "https://www.livemint.com/rss/markets"
}

async def fetch_single_feed(session, source_name, url):
    """Fetches a single XML feed asynchronously and parses it."""
    try:
        async with session.get(url, timeout=10) as response:
            if response.status != 200:
                print(f"Failed to fetch {source_name}: Status {response.status}")
                return []
            
            xml_data = await response.text()
            # feedparser can parse raw XML strings directly
            feed = feedparser.parse(xml_data)
            return parse_feed_entries(feed.entries, source_name)
    except Exception as e:
        print(f"Error reading feed {source_name}: {e}")
        return []

def parse_feed_entries(entries, source_name):
    """Normalizes RSS entries to match your database pipeline schema."""
    last_ts = redis_client.get("rss_last_ts")
    fresh_articles = []
    
    for entry in entries:
        article_id = entry.get("id") or entry.get("link")
        # 1. De-duplicate using published timestamp
        # feedparser automatically extracts structured time into 'published_parsed'
        if hasattr(entry, 'published_parsed') and entry.published_parsed:
            ts = int(time.mktime(entry.published_parsed))
        else:
            ts = int(time.time()) # Fallback to current time if missing

        if last_ts and ts <= int(last_ts):
            continue
        if CacheManager.is_processed("rss", article_id):
            continue
        
        # 2. Map fields to your normalized layout
        normalized = {
            "article_id": entry.get("id") or entry.get("link", str(ts)),
            "title": entry.get("title", ""),
            # RSS fields sometimes use 'summary' or 'description'
            "content": entry.get("summary") or entry.get("description", ""),
            "source": source_name,
            "url": entry.get("link", ""),
            "published_at": datetime.fromtimestamp(ts, tz=timezone.utc),
            "_timestamp": ts # Internal tracker helper
        }
        CacheManager.mark_processed("rss", article_id, ttl=604800) # Keep for 7 days
        
        fresh_articles.append(normalized)
        
    return fresh_articles

async def fetch_news():
    """Concurrently fetches all configured Indian financial RSS feeds."""
    async with aiohttp.ClientSession() as session:
        tasks = [
            fetch_single_feed(session, name, url) 
            for name, url in RSS_FEEDS.items()
        ]
        
        # Run all feed fetches simultaneously
        results = await asyncio.gather(*tasks)
        
        # Flatten the list of lists into a single array
        all_articles = [article for sublist in results for article in sublist]
        
        if not all_articles:
            return []

        # Find the highest timestamp from this current batch to update Redis
        max_ts = max(article["_timestamp"] for article in all_articles)
        redis_client.set("rss_last_ts", max_ts)
        
        # Remove the temporary timestamp helper before returning
        for article in all_articles:
            article.pop("_timestamp", None)
            
        return all_articles