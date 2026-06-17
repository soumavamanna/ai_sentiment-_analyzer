from urllib.parse import urlparse

# Weights configured for Indian Financial Markets and API data streams
CREDIBILITY_WEIGHTS = {
    # Tier 1: Official Exchanges & Direct Disclosures (Maximum Credibility)
    "nseindia.com": 1.00,
    "bseindia.com": 1.00,
    
    # Tier 2: Top Indian Financial Portals (High Credibility)
    "economictimes.indiatimes.com": 0.95,
    "moneycontrol.com": 0.95,
    "livemint.com": 0.95,
    "business-standard.com": 0.90,
    "thehindubusinessline.com": 0.90,
    "cnbctv18.com": 0.90,
    "ndtvprofit.com": 0.90,
    
    # Tier 3: Institutional Trading/Brokerage Insights
    "angelone.in": 0.95,
    "zerodha.com": 0.90,

    # Tier 4: Aggregator APIs & Data Feeds
    "marketaux.com": 0.85,
    "finnhub.io": 0.85,
    "alphavantage.co": 0.85,
    "indianapi.in": 0.80,

    # Global standard baselines
    "reuters.com": 1.00,
    "bloomberg.com": 1.00,
    "wsj.com": 0.95
}

def extract_domain(url: str) -> str:
    """Helper to safely extract the domain from a raw URL or API response string."""
    try:
        # If the URL is just a domain string (e.g., "moneycontrol.com")
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
            
        domain = urlparse(url).netloc.lower()
        
        # Strip 'www.' if present to match our dictionary keys cleanly
        if domain.startswith('www.'):
            domain = domain[4:]
            
        return domain
    except Exception:
        return ""

def get_credibility_score(source: str) -> float:
    """
    Returns a credibility score between 0.0 and 1.0 based on the source domain.
    Defaults to 0.50 for unknown sources to prevent them from entirely hijacking 
    or tanking the sentiment weight.
    """
    domain = extract_domain(source)
    
    # Check for exact matches first
    if domain in CREDIBILITY_WEIGHTS:
        return CREDIBILITY_WEIGHTS[domain]
        
    # Check for partial matches (e.g., "feeds.economictimes.indiatimes.com")
    for known_domain, score in CREDIBILITY_WEIGHTS.items():
        if known_domain in domain:
            return score
            
    # Default baseline for generic news APIs or scraping sources
    return 0.50

# Example usage:
# url_from_feed = "https://www.livemint.com/market/stock-market-news..."
# score = get_credibility_score(url_from_feed) 
# print(f"Weight for sentiment: {score}")  # Output: 0.95