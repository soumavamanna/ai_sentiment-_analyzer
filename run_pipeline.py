import asyncio
from datetime import datetime

# Database Repositories
from database.repositories.financial_signal_repo import save_financial_signals
from database.repositories.article_repo import save_articles

# Phase 1 Ingestion Services
from ingestion.social.social_service import SocialService
from ingestion.announcements.announcement_service import AnnouncementService
from ingestion.news.news_service import get_relevant_news
from ingestion.market.market_service import update_market_data

# Phase 2 & 3 NLP Services
from services.pipeline import FinancialSignalPipeline
from services.social_processor import SocialProcessor
from services.universe_signal_generator import generate_all_company_signals

# Import the new Scheduler module
from infrastructure.scheduler.scheduler import SystemScheduler


def format_for_pipeline(raw_item: dict) -> dict:
    headline = raw_item.get('headline') or raw_item.get('title') or raw_item.get('subject') or ''
    content = raw_item.get('content') or raw_item.get('summary') or raw_item.get('description') or ''
    company_hint = raw_item.get('company_name') or raw_item.get('symbol') or ''

    full_text = f"{company_hint} {headline}. {content}".strip()
    item_id = raw_item.get("id") or raw_item.get("url") or "unknown_id"
    source_url = raw_item.get("source") or raw_item.get("url") or raw_item.get("link") or ""

    return {
        "id": item_id, 
        "source": source_url,
        "text": full_text
    }


async def run():
    print("Initializing Unified NLP Engine and Ingestion Pipeline...")
    
    # 1. Instantiate Services ONCE
    pipeline = FinancialSignalPipeline()
    social_service = SocialService()
    announcement_service = AnnouncementService()
    
    # Initialize the external scheduler
    scheduler = SystemScheduler()

    while True:
        try:
            print("\n" + "="*60)
            print(f"--- Starting Unified Pipeline Cycle @ {datetime.now().strftime('%H:%M:%S')} ---")
            print("="*60)
            
            # STEP A: INGESTION (Phase 1)
            print("\n[1/4] Fetching Raw Market Data & News streams...")
            news = await get_relevant_news()
            save_articles(news) 
            
            rows = await update_market_data() 
            social = await social_service.collect()
            announcements = await announcement_service.collect() 

            print(f" ✓ Saved {len(news)} news articles.")
            print(f" ✓ Saved {rows} market price rows.")
            print(f" ✓ Collected {len(social)} social posts & {len(announcements)} announcements.")

            # STEP B: NLP PROCESSING (Phase 2)
            print("\n[2/4] Running NLP Analysis on unstructured text payload...")
            text_payloads = news + announcements + social
            total_signals_generated = 0

            for item in text_payloads:
                formatted_payload = format_for_pipeline(item)
                
                if len(formatted_payload["text"]) < 10:
                    continue
                
                structured_signals = pipeline.process_article(formatted_payload)
                
                if structured_signals:
                    save_financial_signals(structured_signals)
                    total_signals_generated += len(structured_signals)

            print(f" ✓ Generated & stored {total_signals_generated} structured financial signals.")

            # STEP C: SOCIAL SENTIMENT & MASTER SIGNALS (Phase 3)
            print("\n[3/4] Processing Social Sentiment & Master Signals...")
            
            social_nlp = SocialProcessor()
            social_nlp.process()
            print(" ✓ Social sentiment processed and saved to signals.")
            
            master_signals = generate_all_company_signals()
            strong_buys = [s for s in master_signals if s['signal'] == 'STRONG BUY']
            print(f" ✓ Master Signals Updated. Found {len(strong_buys)} 'STRONG BUY' candidates.")

            # STEP D: SYSTEM MAINTENANCE (Phase 4)
            # Delegate maintenance logic to the scheduler module
            scheduler.run_pending_tasks()

        except Exception as e:
            print(f"\n❌ CRITICAL: Error during pipeline execution pass: {e}")

        print(f"\nCycle complete. Sleeping for 15 minutes...")
        await asyncio.sleep(900)

if __name__ == "__main__":
    asyncio.run(run())