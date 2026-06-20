import asyncio
import yfinance as yf
import numpy as np
import pandas as pd  

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
        threads=False  
    )

async def fetch_market_data():
    NIFTY_SYMBOL = "^NSEI"
    universe = [
        str(x).strip()
        for x in get_universe()
        if str(x).strip()
    ]

    download_symbols = universe + [NIFTY_SYMBOL]

    raw = await asyncio.to_thread(
        _batch_download,
        download_symbols
    )
    if NIFTY_SYMBOL not in raw or raw[NIFTY_SYMBOL].empty:
        print(f"Warning: Failed to fetch {NIFTY_SYMBOL}. Using default momentum.")
        # Create a dummy dataframe or handle gracefully
        nifty_df = pd.DataFrame(index=raw.index, columns=["Close"]).fillna(1.0)
    else:
        nifty_df = raw[NIFTY_SYMBOL].copy()
    
    nifty_df = raw[NIFTY_SYMBOL].copy()

    # FIX 1: Added fill_method=None to remove FutureWarning
    nifty_df["nifty_return_20d"] = nifty_df["Close"].pct_change(20, fill_method=None)

    market_rows = []

    for ticker in universe:
        try:
            if ticker not in raw.columns.levels[0]:
                continue

            df = raw[ticker].copy()

            if len(df) < 30:
                continue

            # FIX 1: Added fill_method=None to remove FutureWarnings
            df["return_1d"] = df["Close"].pct_change(1, fill_method=None)
            df["return_5d"] = df["Close"].pct_change(5, fill_method=None)
            df["return_20d"] = df["Close"].pct_change(20, fill_method=None)

            df["volatility_20d"] = (
                df["Close"]
                .pct_change(fill_method=None)
                .rolling(20)
                .std()
                * np.sqrt(252)
            )

            df["rsi_14"] = compute_rsi(df["Close"])
            df["atr_14"] = compute_atr(df)

            df["volume_ratio"] = (
                df["Volume"]
                /
                df["Volume"].rolling(20).mean()
            )
            df["prev_close"] = df["Close"].shift(1)

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
                df["return_20d"] - df["nifty_return_20d"]
            )
            df["dollar_volume"] = (
                df["Close"] * df["Volume"]
            )
            df["volume_surge"] = (
                df["Volume"]
                /
                df["Volume"].rolling(60).mean()
            )

            latest = df.iloc[-1]

            # FIX 2: Added pd.notna() fallbacks to prevent NaN casting crashes
            market_rows.append({
                "ticker": ticker,
                "market_date": latest.name.date(),
                "open": float(latest["Open"]) if pd.notna(latest["Open"]) else 0.0,
                "high": float(latest["High"]) if pd.notna(latest["High"]) else 0.0,
                "low": float(latest["Low"]) if pd.notna(latest["Low"]) else 0.0,
                "close": float(latest["Close"]) if pd.notna(latest["Close"]) else 0.0,
                "volume": int(latest["Volume"]) if pd.notna(latest["Volume"]) else 0,
                "return_1d": float(latest["return_1d"]) if pd.notna(latest["return_1d"]) else 0.0,
                "return_5d": float(latest["return_5d"]) if pd.notna(latest["return_5d"]) else 0.0,
                "return_20d": float(latest["return_20d"]) if pd.notna(latest["return_20d"]) else 0.0,
                "volatility_20d": float(latest["volatility_20d"]) if pd.notna(latest["volatility_20d"]) else 0.0,
                "rsi_14": float(latest["rsi_14"]) if pd.notna(latest["rsi_14"]) else 50.0, # Default RSI to neutral 50
                "atr_14": float(latest["atr_14"]) if pd.notna(latest["atr_14"]) else 0.0,
                "volume_ratio": float(latest["volume_ratio"]) if pd.notna(latest["volume_ratio"]) else 1.0,
                "gap_pct": float(latest["gap_pct"]) if pd.notna(latest["gap_pct"]) else 0.0,
                "relative_strength": float(latest["relative_strength"]) if pd.notna(latest["relative_strength"]) else 0.0,
                "dollar_volume": float(latest["dollar_volume"]) if pd.notna(latest["dollar_volume"]) else 0.0,
                "volume_surge": float(latest["volume_surge"]) if pd.notna(latest["volume_surge"]) else 1.0
            })

        except Exception as e:
            print(f"Error processing {ticker}: {e}")

    return market_rows