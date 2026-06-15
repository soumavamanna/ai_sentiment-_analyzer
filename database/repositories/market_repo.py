from sqlalchemy import text

from database.db import engine


def save_market_data(
    rows
):

    query = text("""
    INSERT INTO market_prices
    (
        ticker,
        market_date,
        open,
        high,
        low,
        close,
        volume
    )
    VALUES
    (
        :ticker,
        :market_date,
        :open,
        :high,
        :low,
        :close,
        :volume
    )
    ON CONFLICT
    (
        ticker,
        market_date
    )
    DO NOTHING
    """)

    with engine.begin() as conn:

        for row in rows:

            conn.execute(
                query,
                row
            )