import aiohttp
import asyncio
from datetime import datetime, timezone
from infrastructure.cache.redis_client import redis_client
from utils.cache_manager import CacheManager
from services.universe_service import get_universe

class TradingQNACollector:
    def __init__(self):
        # Base search endpoint for Discourse
        self.base_url = "https://tradingqna.com/search/query.json"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "application/json"
        }

    async def fetch_ticker_discussions(self, session, ticker):
        """Fetches the latest forum posts for a specific ticker."""
        
        # Clean the ticker (e.g., RELIANCE.NS -> RELIANCE)
        clean_ticker = ticker.split('.')[0]
        
        # Construct the query parameter. We sort by latest.
        # Example query: https://tradingqna.com/search/query.json?term=RELIANCE order:latest
        params = {
            "term": f"{clean_ticker} order:latest"
        }

        try:
            async with session.get(self.base_url, headers=self.headers, params=params, timeout=15) as response:
                if response.status != 200:
                    print(f"TradingQ&A returned status {response.status} for {ticker}")
                    return []
                
                data = await response.json()
        except Exception as e:
            print(f"Error fetching TradingQ&A data for {ticker}: {e}")
            return []

        posts_data = []
        
        # Discourse search returns a "posts" list and a "topics" list.
        # The actual text is inside the "posts" list.
        posts = data.get("posts", [])
        
        for post in posts[:20]:  # Only grab the latest 20 hits per stock to avoid spam
            post_id = str(post.get("id"))
            text = post.get("blurb", "")  # 'blurb' contains the highlighted text snippet
            author = post.get("username", "unknown")
            like_count = post.get("like_count", 0)
            created_at_str = post.get("created_at")

            if not text:
                continue

            # Deduplication
            if CacheManager.is_processed("tradingqna", post_id):
                continue

            # Parse ISO 8601 Timestamp from Discourse
            dt_obj = None
            if created_at_str:
                try:
                    dt_obj = datetime.strptime(created_at_str[:19], "%Y-%m-%dT%H:%M:%S")
                    dt_obj = dt_obj.replace(tzinfo=timezone.utc)
                except ValueError:
                    pass

            posts_data.append({
                "post_id": post_id,
                "platform": "tradingqna",
                "author": author,
                "text": f"[{clean_ticker}] {text}", # Prefix the text with the ticker for context
                "timestamp": dt_obj,
                "engagement": like_count
            })

            CacheManager.mark_processed("tradingqna", post_id)

        return posts_data

    async def run_collection(self):
        """Runs the asynchronous loop across your entire Universe."""
        universe = get_universe()
        all_posts = []

        print(f"Starting TradingQ&A scrape for {len(universe)} tickers...")

        async with aiohttp.ClientSession() as session:
            tasks = [self.fetch_ticker_discussions(session, ticker) for ticker in universe]
            
            # Gather results concurrently
            results = await asyncio.gather(*tasks, return_exceptions=True)

            for result in results:
                if isinstance(result, list):
                    all_posts.extend(result)

        return all_posts