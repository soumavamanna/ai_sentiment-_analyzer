from ingestion.market.market_collector import (
    fetch_market_data
)

from database.repositories.market_repo import (
    save_market_data
)


def update_market_data():

    data = fetch_market_data()

    save_market_data(data)

    return len(data)