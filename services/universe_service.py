from pathlib import Path

from utils.file_loader import load_tickers

TICKER_DIR = Path(
    "services/data/tickers"
)

def get_universe():

    universe = set()

    for file in TICKER_DIR.glob(
        "*.csv"
    ):
        universe.update(
            load_tickers(file)
        )

    return universe