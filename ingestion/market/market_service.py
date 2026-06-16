from ingestion.market.market_collector import fetch_market_data
from database.repositories.market_repo import save_market_data

async def update_market_data():
    """Triggers the asynchronous asset valuation pipeline and commits to database."""
    # Await the updated async market downloader
    data = await fetch_market_data()

    if data:
        # Assuming save_market_data handles database connection contexts synchronously
        save_market_data(data)

    return len(data)