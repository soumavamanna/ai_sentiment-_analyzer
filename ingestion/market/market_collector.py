import asyncio
import yfinance as yf
import numpy as np

from services.universe_service import get_universe
from services.technical_factors import (
    compute_rsi,
    compute_atr
)
def _batch_download(tickers):

    return yf.download(
        tickers=tickers,
        period="6mo",
        group_by="ticker",
        auto_adjust=False,
        progress=False,
        threads=True
    )
async def fetch_market_data():
    NIFTY_SYMBOL = "^NSEI"
    universe = [
        str(x).strip()
        for x in get_universe()
        if str(x).strip()
    ]

    download_symbols = universe + [
        NIFTY_SYMBOL
    ]

    raw = await asyncio.to_thread(
        _batch_download,
        download_symbols
    )
    nifty_df = raw[NIFTY_SYMBOL].copy()

    nifty_df["nifty_return_20d"] = (
        nifty_df["Close"]
        .pct_change(20)
    )

    market_rows = []

    for ticker in universe:

        try:

            if ticker not in raw.columns.levels[0]:
                continue

            df = raw[ticker].copy()

            if len(df) < 30:
                continue

            df["return_1d"] = (
                df["Close"].pct_change(1)
            )

            df["return_5d"] = (
                df["Close"].pct_change(5)
            )

            df["return_20d"] = (
                df["Close"].pct_change(20)
            )

            df["volatility_20d"] = (
                df["Close"]
                .pct_change()
                .rolling(20)
                .std()
                * np.sqrt(252)
            )

            df["rsi_14"] = compute_rsi(
                df["Close"]
            )

            df["atr_14"] = compute_atr(
                df
            )

            df["volume_ratio"] = (
                df["Volume"]
                /
                df["Volume"]
                .rolling(20)
                .mean()
            )
            df["prev_close"] = (
                df["Close"]
                .shift(1)
            )

            df["gap_pct"] = (
                (df["Open"] - df["prev_close"])
                /
                df["prev_close"]
            )
            df = df.join(
                nifty_df["nifty_return_20d"],
                how="left"
            )

            df["relative_strength"] = (
                df["return_20d"]
                -
                df["nifty_return_20d"]
            )
            df["dollar_volume"] = (
                df["Close"]
                *
                df["Volume"]
            )
            df["volume_surge"] = (
                df["Volume"]
                /
                df["Volume"]
                .rolling(60)
                .mean()
            )

            latest = df.iloc[-1]

            market_rows.append({

                "ticker": ticker,

                "market_date":
                    latest.name.date(),

                "open":
                    float(latest["Open"]),

                "high":
                    float(latest["High"]),

                "low":
                    float(latest["Low"]),

                "close":
                    float(latest["Close"]),

                "volume":
                    int(latest["Volume"]),

                "return_1d":
                    float(latest["return_1d"]),

                "return_5d":
                    float(latest["return_5d"]),

                "return_20d":
                    float(latest["return_20d"]),

                "volatility_20d":
                    float(
                        latest["volatility_20d"]
                    ),

                "rsi_14":
                    float(
                        latest["rsi_14"]
                    ),

                "atr_14":
                    float(
                        latest["atr_14"]
                    ),
                "volume_ratio":
                    float(
                        latest["volume_ratio"]
                    ),
                 "gap_pct":
                    float(
                        latest["gap_pct"]
                    ),

                "relative_strength":
                    float(
                        latest["relative_strength"]
                    ),

                "dollar_volume":
                    float(
                        latest["dollar_volume"]
                    ),
                 "volume_surge":
                    float(
                        latest["volume_surge"]
                    )
                })

        except Exception as e:

            print(
                f"Error processing {ticker}: {e}"
            )

    return market_rows