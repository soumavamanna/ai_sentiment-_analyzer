# main.py

from services.pipeline import FinancialSignalPipeline
from database.repositories.financial_signal_repo import save_financial_signals

def main():
    pipeline = FinancialSignalPipeline()

    # A mock payload simulating a major Phase 3 catalyst
    mock_incoming_payload = {
        "id": "news_test_001",
        "source": "https://economictimes.indiatimes.com/markets/test",
        "text": "Reliance Industries announces a massive share buyback plan and beats Q4 earnings estimates. Trading volume surged."
    }

    print("Processing incoming Phase 3 test payload...")
    structured_signals = pipeline.process_article(mock_incoming_payload)
    
    if structured_signals:
        print(f"\n✅ Generated {len(structured_signals)} structured market signals.")
        
        # Print results to verify output formatting and Explainability Engine
        for signal in structured_signals:
            print("\n" + "="*50)
            print(f"[{signal['ticker']}] COMPOSITE SCORE: {signal['composite_score']}/100")
            print("="*50)
            print(signal['explanation'])
            print("="*50)

        # Commit directly using SQLAlchemy
        save_financial_signals(structured_signals)
        print("\n✅ Successfully committed Phase 3 signals to PostgreSQL.")
    else:
        print("❌ No signals generated.")

if __name__ == "__main__":
    main()