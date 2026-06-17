from sqlalchemy import text
from database.db import engine


def get_company_context(ticker: str):

    query = text("""
    SELECT
        c.ticker,

        mp.return_1d,
        mp.return_5d,
        mp.return_20d,
        mp.rsi_14,
        mp.volume_ratio,
        mp.volatility_20d,

        COALESCE(news.news_count,0) news_count,
        COALESCE(news.news_sentiment,0) news_sentiment,

        COALESCE(ann.announcement_count,0) announcement_count,
        COALESCE(ann.announcement_score,0) announcement_score,

        COALESCE(soc.social_count,0) social_count,
        COALESCE(soc.social_sentiment,0) social_sentiment

    FROM nse_company_metadata c

    LEFT JOIN LATERAL (
        SELECT *
        FROM market_prices
        WHERE ticker = c.ticker
        ORDER BY market_date DESC
        LIMIT 1
    ) mp ON TRUE

    LEFT JOIN LATERAL (
        SELECT
            COUNT(*) news_count,
            AVG(weighted_sentiment_score) news_sentiment
        FROM financial_signals
        WHERE ticker = c.ticker
        AND processed_at >= NOW() - INTERVAL '7 days'
    ) news ON TRUE

    LEFT JOIN LATERAL (
        SELECT
            COUNT(*) announcement_count,

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
            ) announcement_score

        FROM announcements
        WHERE symbol = c.ticker
        AND timestamp >= NOW() - INTERVAL '30 days'
    ) ann ON TRUE

    LEFT JOIN LATERAL (
        SELECT
            COUNT(*) social_count,
            AVG(sentiment_score) social_sentiment
        FROM social_signals
        WHERE ticker = c.ticker
        AND created_at >= NOW() - INTERVAL '7 days'
    ) soc ON TRUE

    WHERE c.ticker = :ticker
    """)

    with engine.connect() as conn:

        row = conn.execute(
            query,
            {"ticker": ticker}
        ).mappings().first()

    return dict(row) if row else None