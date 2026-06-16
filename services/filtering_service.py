from services.universe_service import get_universe, get_ticker_aliases

UNIVERSE = get_universe()
# Generate the alias mapping dynamically from your CSV
TICKER_ALIASES = get_ticker_aliases()

def article_relevant(article):
    # Combine title and content to search against
    text = (
        article.get("title", "") 
        + " " 
        + article.get("content", "")
    ).upper()

    # If the text is completely empty, fail fast
    if not text.strip():
        return False

    for ticker in UNIVERSE:
        # Strip '.NS' and clean up spaces
        base_ticker = ticker.replace(".NS", "").strip().upper()

        # 1. Check for the raw base ticker (e.g., "ITC")
        if base_ticker in text:
            return True

        # 2. Check the dynamic aliases from your CSV
        aliases = TICKER_ALIASES.get(base_ticker, [])
        for alias in aliases:
            if alias in text:
                return True

    return False