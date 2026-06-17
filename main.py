from services.pipeline import FinancialSignalPipeline
from database.db_manager import DatabaseManager

def main():
    # Initialize the engine modules and the database backend
    pipeline = FinancialSignalPipeline()
    db = DatabaseManager()

    # Mock raw incoming payload from an RSS parser or Marketaux webhook
    mock_incoming_payload = {
        "id": "news_98324",
        "source": "https://www.moneycontrol.com/news/business/markets/livemint-news-update",
        "text": "Reliance Industries shares surge as RIL announces a massive share buyback plan alongside a major earnings beat in Q4."
    }

    print("Processing incoming news content...")
    
    # 1. Run raw text through the NLP and entity mapping components
    structured_signals = pipeline.process_article(mock_incoming_payload)
    
    if structured_signals:
        print(f"Generated {len(structured_signals)} structured market signals.")
        
        # 2. Persist the signals cleanly to SQLite
        db.insert_signals(structured_signals)
        print("Successfully committed signals to relational database storage.")
        
        # Print results to verify output formatting
        for signal in structured_signals:
            print(f"\nSaved Signal Details [{signal['ticker']}]:")
            print(f" - Sentiment: {signal['sentiment']} ({signal['sentiment_confidence']})")
            print(f" - Event Group: {signal['event_type']} ({signal['event_confidence']})")
            print(f" - Novelty Score: {signal['novelty_score']}")
    else:
        print("No recognized NSE ticker found or article didn't yield actionable signals.")

if __name__ == "__main__":
    main()