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
        volume,

        return_1d,
        return_5d,
        return_20d,

        volatility_20d,

        rsi_14,

        atr_14,

        volume_ratio,
        gap_pct,
        relative_strength,
        dollar_volume,
        volume_surge
    )
    VALUES
    (
        :ticker,
        :market_date,
        :open,
        :high,
        :low,
        :close,
        :volume,
        :return_1d,
        :return_5d,
        :return_20d,

        :volatility_20d,

        :rsi_14,

        :atr_14,

        :volume_ratio,
        :gap_pct,
        :relative_strength,
        :dollar_volume,
        :volume_surge
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