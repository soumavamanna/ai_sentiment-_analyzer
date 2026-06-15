import pandas as pd

def load_tickers(filepath):

    df = pd.read_csv(filepath)

    return set(
        df["ticker"].tolist()
    )