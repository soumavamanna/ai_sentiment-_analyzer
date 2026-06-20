from services.ticker_resolver import TickerResolver

# Initialize the resolver once at the module level to prevent overhead on every article check
resolver = TickerResolver()

def article_relevant(article):
    # Combine title and content to search against
    text = (
        article.get("title", "") 
        + " " 
        + article.get("content", "")
    )

    # If the text is completely empty, fail fast
    if not text.strip():
        return False

    # Leverage the FlashText KeywordProcessor to find strict, word-bounded matches
    matched_companies = resolver.extract_ticker_info(text)
    
    # If the resolver found at least one valid company from the metadata, it's relevant
    if matched_companies:
        return True

    return False