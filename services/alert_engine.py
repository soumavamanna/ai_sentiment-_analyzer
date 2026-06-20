# services/alert_engine.py

from database.db import engine
from sqlalchemy import text

def generate_daily_alerts():
    """
    Phase 3.5 Alert Engine: Fetches the Top 10 signals generated today.
    """
    query = text("""
        SELECT ticker, composite_score, event_type, explanation, processed_at
        FROM financial_signals
        WHERE processed_at >= NOW() - INTERVAL '24 hours'
        ORDER BY composite_score DESC
        LIMIT 10;
    """)
    
    with engine.connect() as conn:
        results = conn.execute(query).fetchall()
        
    print("\n" + "="*60)
    print("🔥 TOP 10 EVENT-DRIVEN OPPORTUNITIES TODAY 🔥")
    print("="*60)
    
    if not results:
        print("No signals generated in the last 24 hours.")
        return

    for row in results:
        print(f"\n[{row.ticker}] COMPOSITE SCORE: {row.composite_score}/100")
        print(f"Catalyst: {row.event_type.title()}")
        print("-" * 40)
        print(row.explanation)
        print("=" * 60)

if __name__ == "__main__":
    generate_daily_alerts()