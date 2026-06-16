from ingestion.social.tradingqna_collector import TradingQNACollector
from database.repositories.social_repo import save_social_posts

class SocialService:
    def __init__(self):
        # You can keep Moneycontrol here if you fixed the API issue, 
        # or just use TradingQ&A.
        self.tradingqna = TradingQNACollector()

    async def collect(self):
        data = []

        try:
            # Await the TradingQ&A scraper
            qna_posts = await self.tradingqna.run_collection()
            data.extend(qna_posts)
        except Exception as e:
            print(f"Error executing TradingQ&A collector: {e}")

        # Save to PostgreSQL if posts were found
        if data:
            # Assuming save_social_posts handles synchronous SQLAlchemy commits
            save_social_posts(data)
            print(f"Successfully saved {len(data)} TradingQ&A posts.")
        else:
            print("No new social posts found.")

        return data