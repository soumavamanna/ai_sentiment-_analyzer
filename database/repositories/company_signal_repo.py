# database/repositories/company_signal_repo.py

from sqlalchemy import text
from database.db import engine

def get_company_context(ticker: str):
    query = text("""
    WITH target_company AS (
        SELECT CAST(:ticker AS TEXT) AS ticker
    )
    SELECT
        c.ticker,
        mp.return_1d,
        mp.return_5d,
        mp.return_20d,
        mp.rsi_14,
        mp.volume_ratio,
        mp.volatility_20d,

        COALESCE(news.news_count,0) AS news_count,
        COALESCE(news.news_sentiment,0) AS news_sentiment,

        COALESCE(ann.announcement_count,0) AS announcement_count,
        COALESCE(ann.announcement_score,0) AS announcement_score,

        COALESCE(soc.social_count,0) AS social_count,
        COALESCE(soc.social_sentiment,0) AS social_sentiment

    FROM target_company c

    -- 1. Get Latest Market Prices
    LEFT JOIN LATERAL (
        SELECT *
        FROM market_prices
        WHERE ticker = c.ticker
        ORDER BY market_date DESC
        LIMIT 1
    ) mp ON TRUE

    -- 2. Get News Sentiment (Excluding Social)
    LEFT JOIN LATERAL (
        SELECT
            COUNT(*) AS news_count,
            AVG(weighted_sentiment_score) AS news_sentiment
        FROM financial_signals
        WHERE ticker = c.ticker
        AND event_type != 'social_chatter'
        AND processed_at >= NOW() - INTERVAL '7 days'
    ) news ON TRUE

    -- 3. Get Announcements Impact
    LEFT JOIN LATERAL (
        SELECT
            COUNT(*) AS announcement_count,
            AVG(
                CASE
                    WHEN lower(subject) LIKE '%buyback%' THEN 1
                    WHEN lower(subject) LIKE '%dividend%' THEN 0.7
                    WHEN lower(subject) LIKE '%order%' THEN 0.6
                    WHEN lower(subject) LIKE '%acquisition%' THEN 0.5
                    WHEN lower(subject) LIKE '%penalty%' THEN -0.7
                    WHEN lower(subject) LIKE '%fraud%' THEN -1
                    ELSE 0
                END
            ) AS announcement_score
        FROM announcements
        WHERE symbol = c.ticker
        AND timestamp >= NOW() - INTERVAL '30 days'
    ) ann ON TRUE

    -- 4. Get Social Sentiment
    LEFT JOIN LATERAL (
        SELECT
            COUNT(*) AS social_count,
            AVG(weighted_sentiment_score) AS social_sentiment
        FROM financial_signals
        WHERE ticker = c.ticker
        AND event_type = 'social_chatter'
        AND processed_at >= NOW() - INTERVAL '7 days'
    ) soc ON TRUE
    """)

    with engine.connect() as conn:
        row = conn.execute(query, {"ticker": ticker}).mappings().first()

    return dict(row) if row else None