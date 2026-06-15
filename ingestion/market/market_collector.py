import yfinance as yf

from services.universe_service import (
    get_universe
)

def fetch_market_data():

    universe = get_universe()

    market_data = []

    for raw_ticker in universe:
        ticker = str(raw_ticker).strip()
        
       
        if not ticker:
            continue
        data = yf.download(
            ticker,
            period="5d",
            progress=False
        )
        if data.empty:
            print(f"⚠️ Skipping {ticker}: No data found on Yahoo Finance.")
            continue

        latest = data.iloc[-1]

        market_data.append({
            "ticker": ticker,
            "open": float(
                latest["Open"]
            ),
            "high": float(
                latest["High"]
            ),
            "low": float(
                latest["Low"]
            ),
            "close": float(
                latest["Close"]
            ),
            "volume": int(
                latest["Volume"]
            )
        })

    return market_data