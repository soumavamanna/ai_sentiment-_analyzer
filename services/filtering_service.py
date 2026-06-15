from services.universe_service import (
    get_universe
)

UNIVERSE = get_universe()

def article_relevant(article):

    text = (
        article.get("headline","")
        + " "
        + article.get("summary","")
    ).upper()

    for ticker in UNIVERSE:

        company = ticker.replace(
            ".NS",
            ""
        )

        if company in text:
            return True

    return False