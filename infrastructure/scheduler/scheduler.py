import asyncio
from database.repositories.article_repo import save_articles
from ingestion.social.social_service import SocialService
from ingestion.announcements.announcement_service import AnnouncementService
from ingestion.news.news_service import get_relevant_news
from ingestion.market.market_service import update_market_data

async def run():
    # Instantiate your services ONCE outside the loop to save memory overhead
    social_service = SocialService()
    announcement_service = AnnouncementService()

    while True:
        try:
            print("\n--- Starting Ingestion Cycle ---")
            
            # 1. Fetch and save news articles
            news = await get_relevant_news()
            save_articles(news)
            
            # 2. Update equity market prices 
            # (If update_market_data is async, add 'await' here)
            rows = await update_market_data() 
            
            # 3. Fetch social board discussions (Awaited)
            social = await social_service.collect()
            
            # 4. Fetch exchange corporate filings
            # FIX: Added 'await' assuming collect() handles async HTTP networking
            announcements = await announcement_service.collect() 

            # Log operational updates
            print(f"Saved {len(news)} news articles.")
            print(f"Saved {rows} market price rows.")
            print(f"Social posts collected: {len(social)}")
            print(f"Announcements collected: {len(announcements)}")
            
        except Exception as e:
            # Wrap the iteration in a try-except block so a single network timeout 
            # or database glitch doesn't kill your entire background service permanently.
            print(f"CRITICAL: Error during ingestion execution pass: {e}")

        print("Ingestion pass complete. Sleeping for 15 minutes...")
        await asyncio.sleep(900)