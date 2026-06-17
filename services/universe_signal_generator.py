from sqlalchemy import text

from database.db import engine

from services.company_signal_generator import (
    generate_company_signal
)


def generate_all_company_signals():

    query = text("""
    SELECT ticker
    FROM nse_company_metadata
    """)

    with engine.connect() as conn:

        tickers = [
            row[0]
            for row in conn.execute(query)
        ]

    signals = []

    for ticker in tickers:

        signal = generate_company_signal(
            ticker
        )

        if signal:

            signals.append(signal)

    return signals