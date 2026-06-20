# database/repositories/financial_signal_repo.py

from sqlalchemy import text
from database.db import engine

def save_financial_signals(signals: list[dict]):
    """
    Bulk inserts Phase 3 structured financial signals into PostgreSQL.
    """
    if not signals:
        return

    query = text("""
        INSERT INTO financial_signals (
            article_id, ticker, sentiment, sentiment_confidence, weighted_sentiment_score, 
            event_type, event_confidence, novelty_score, source_credibility, 
            composite_score, explanation
        ) VALUES (
            :article_id, :ticker, :sentiment, :sentiment_confidence, :weighted_sentiment_score, 
            :event_type, :event_confidence, :novelty_score, :source_credibility, 
            :composite_score, :explanation
        )
        ON CONFLICT (article_id, ticker) 
        DO UPDATE SET 
            composite_score = EXCLUDED.composite_score,
            weighted_sentiment_score = EXCLUDED.weighted_sentiment_score
        """)

    with engine.begin() as conn:
        for signal in signals:
            conn.execute(query, signal)