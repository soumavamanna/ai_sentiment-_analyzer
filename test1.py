from services.social_processor import SocialProcessor
from database.db import engine
from sqlalchemy import text

def run_test():
    print("🧠 Spinning up FinBERT Social Processor...")
    processor = SocialProcessor()
    
    # This will read from social_posts and write to financial_signals
    processor.process()
    print("✅ Social processing complete.")
    
    # Verify the database commit using the CORRECT Phase 3 schema
    query = text("""
        SELECT ticker, composite_score, weighted_sentiment_score 
        FROM financial_signals 
        WHERE event_type = 'social_chatter' 
        ORDER BY processed_at DESC 
        LIMIT 5;
    """)
    
    with engine.connect() as conn:
        results = conn.execute(query).fetchall()
        
    if results:
        print("\n📊 Latest Social Signals in PostgreSQL:")
        for row in results:
            print(f"[{row.ticker}] Composite Score: {row.composite_score}/100 | Weighted Sentiment: {row.weighted_sentiment_score}")
    else:
        print("\n❌ No social signals found in the database.")

if __name__ == "__main__":
    run_test()