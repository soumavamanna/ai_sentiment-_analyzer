import asyncio
from database.db_manager import DatabaseManager
from services.pipeline import FinancialSignalPipeline

# Phase 1 Ingestion Imports
from database.repositories.article_repo import save_articles
from ingestion.social.social_service import SocialService
from ingestion.announcements.announcement_service import AnnouncementService
from ingestion.news.news_service import get_relevant_news
from ingestion.market.market_service import update_market_data

def format_for_pipeline(raw_item: dict) -> dict:
    """
    Standardizes Phase 1 dictionary outputs into the format Phase 2 expects,
    accommodating different key names from various scrapers/APIs.
    """
    # Fallback chains for headlines/titles
    headline = raw_item.get('headline') or raw_item.get('title') or raw_item.get('subject') or ''
    
    # Fallback chains for body text
    content = raw_item.get('content') or raw_item.get('summary') or raw_item.get('description') or ''
    
    # If the API provides the exact company name, inject it so the TickerResolver cannot miss it
    company_hint = raw_item.get('company_name') or raw_item.get('symbol') or ''

    full_text = f"{company_hint} {headline}. {content}".strip()
    
    # Grab the best available ID and URL
    item_id = raw_item.get("id") or raw_item.get("url") or "unknown_id"
    source_url = raw_item.get("source") or raw_item.get("url") or raw_item.get("link") or ""

    return {
        "id": item_id, 
        "source": source_url,
        "text": full_text
    }
async def run():
    # 1. Instantiate Phase 2 Services (NLP Engine & PostgreSQL)
    print("Initializing NLP Engine and PostgreSQL connection...")
    db = DatabaseManager()
    pipeline = FinancialSignalPipeline()

    # 2. Instantiate Phase 1 Services (Data Ingestion)
    social_service = SocialService()
    announcement_service = AnnouncementService()

    while True:
        try:
            print("\n--- Starting Ingestion & NLP Cycle ---")
            
            # Step A: Fetch all raw data (Phase 1)
            news = await get_relevant_news()
            save_articles(news) # Saves raw data to repo
            
            rows = await update_market_data() 
            social = await social_service.collect()
            announcements = await announcement_service.collect() 

            # Step B: Combine textual data for NLP processing
            # You can also add `social` here if you want to analyze tweets/posts!
            text_payloads = news + announcements 
            total_signals_generated = 0

            # Step C: Process through the NLP pipeline (Phase 2)
            print(f"Passing {len(text_payloads)} items to the NLP Engine...")
            for item in text_payloads:
                formatted_payload = format_for_pipeline(item)
                
                # Skip empty content
                if len(formatted_payload["text"]) < 10:
                    continue
                
                structured_signals = pipeline.process_article(formatted_payload)
                print(f" [DEBUG SCANNING]: {formatted_payload['text'][:100]}...")
                if structured_signals:

                    print("\n=== SIGNALS GENERATED ===")
                    print(f"Count: {len(structured_signals)}")

                    for s in structured_signals[:5]:
                        print(s)

                    db.insert_signals(structured_signals)
                    total_signals_generated += len(structured_signals)
                else:
                    print("No signals generated.")
                    
              
            # Step D: Log Cycle Summary
            print("\n[Cycle Summary]")
            print(f" ✓ Saved {len(news)} raw news articles.")
            print(f" ✓ Saved {rows} market price rows.")
            print(f" ✓ Collected {len(social)} social posts & {len(announcements)} announcements.")
            print(f" ➔ Generated & stored {total_signals_generated} structured financial signals in PostgreSQL.")
            
        except Exception as e:
            print(f"CRITICAL: Error during pipeline execution pass: {e}")

        print("\nIngestion pass complete. Sleeping for 15 minutes...")
        await asyncio.sleep(900)

if __name__ == "__main__":
    # Execute the async loop
    asyncio.run(run())