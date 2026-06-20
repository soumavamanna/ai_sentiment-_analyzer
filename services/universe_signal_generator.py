from services.universe_service import get_universe
from services.company_signal_generator import generate_company_signal

def generate_all_company_signals():
    # Pull the universe directly from the CSV instead of the missing database table
    tickers = get_universe()
    signals = []

    for ticker in tickers:
        signal = generate_company_signal(ticker)
        if signal:
            signals.append(signal)

    return signals