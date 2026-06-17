from sqlalchemy import text
from database.db import engine


def get_market_context(ticker: str):

    query = text("""
    SELECT
        ticker,

        close,

        return_1d,
        return_5d,
        return_20d,

        volatility_20d,

        rsi_14,

        atr_14,

        volume_ratio,

        gap_pct

    FROM market_prices
    WHERE ticker = :ticker
    ORDER BY market_date DESC
    LIMIT 1
    """)

    with engine.connect() as conn:

        row = conn.execute(
            query,
            {"ticker": ticker}
        ).mappings().first()

    return dict(row) if row else None