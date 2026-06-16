import asyncio
import yfinance as yf
from services.universe_service import get_universe

def _blocking_download(ticker):
    """Helper function to execute the blocking yfinance network call safely in a thread."""
    return yf.download(
        ticker,
        period="5d",
        auto_adjust=False,
        progress=False
    )

async def fetch_market_data():
    """Asynchronously fetches current market data for your entire ticker universe concurrently."""
    universe = get_universe()
    market_data = []

    async def process_ticker(raw_ticker):
        ticker = str(raw_ticker).strip()
        if not ticker:
            return None

        try:
            # Offload the blocking yfinance download call to a separate background thread
            data = await asyncio.to_thread(_blocking_download, ticker)
            
            if data.empty:
                print(f"⚠️ Skipping {ticker}: No data found on Yahoo Finance.")
                return None

            latest = data.iloc[-1]

            # Parse safe scalar values handling potential pandas MultiIndex variations
            return {
                "ticker": ticker,
                "market_date": latest.name.date(),
                "open": float(latest["Open"].iloc[0]) if hasattr(latest["Open"], "iloc") else float(latest["Open"]),
                "high": float(latest["High"].iloc[0]) if hasattr(latest["High"], "iloc") else float(latest["High"]),
                "low": float(latest["Low"].iloc[0]) if hasattr(latest["Low"], "iloc") else float(latest["Low"]),
                "close": float(latest["Close"].iloc[0]) if hasattr(latest["Close"], "iloc") else float(latest["Close"]),
                "volume": int(latest["Volume"].iloc[0]) if hasattr(latest["Volume"], "iloc") else int(latest["Volume"])
            }
        except Exception as e:
            print(f"❌ Error downloading market data for {ticker}: {e}")
            return None

    # Trigger downloads for all tickers concurrently using asyncio.gather
    tasks = [process_ticker(ticker) for ticker in universe]
    results = await asyncio.gather(*tasks)

    # Filter out None results from skipped/failed tickers
    market_data = [res for res in results if res is not None]
    return market_data