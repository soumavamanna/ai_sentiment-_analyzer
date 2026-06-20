# services/company_signal_generator.py

from database.repositories.company_signal_repo import get_company_context

def generate_company_signal(ticker: str):
    ctx = get_company_context(ticker)

    if not ctx:
        return None
    print(f"\n[AUDIT: {ticker}]")
    print(f"  News Count: {ctx.get('news_count')} | Sentiment: {ctx.get('news_sentiment')}")
    print(f"  Social Count: {ctx.get('social_count')} | Sentiment: {ctx.get('social_sentiment')}")
    print(f"  Announcements: {ctx.get('announcement_count')} | Impact: {ctx.get('announcement_score')}")
    print(f"  Market Data: Vol Ratio: {ctx.get('volume_ratio')} | RSI: {ctx.get('rsi_14')}")
    # 1. Safely extract and cast to float to prevent Decimal vs Float crashes
    news_sentiment = float(ctx.get("news_sentiment") or 0.0)
    announcement_score = float(ctx.get("announcement_score") or 0.0)
    social_sentiment = float(ctx.get("social_sentiment") or 0.0)
    
    return_5d = float(ctx.get("return_5d") or 0.0)
    return_20d = float(ctx.get("return_20d") or 0.0)
    rsi = float(ctx.get("rsi_14") or 50.0) # Default RSI to neutral 50
    volume_ratio = float(ctx.get("volume_ratio") or 1.0)
    volatility_20d = float(ctx.get("volatility_20d") or 0.0)

    score = 0.0

    # --------------------
    # NEWS
    # --------------------
    score += (news_sentiment * 30.0)

    # --------------------
    # ANNOUNCEMENTS
    # --------------------
    score += (announcement_score * 25.0)

    # --------------------
    # SOCIAL
    # --------------------
    score += (social_sentiment * 15.0)

    # --------------------
    # PRICE MOMENTUM
    # --------------------
    score += (return_5d * 100.0 * 0.10)
    score += (return_20d * 100.0 * 0.05)

    # --------------------
    # RSI
    # --------------------
    if rsi < 30.0:
        score += 10.0
    elif rsi > 70.0:
        score -= 10.0

    # --------------------
    # VOLUME CONFIRMATION
    # --------------------
    if volume_ratio > 2.0:
        score += 5.0

    # --------------------
    # VOLATILITY PENALTY
    # --------------------
    if volatility_20d > 0.08:
        score -= 5.0

    # --------------------
    # SIGNAL LABEL
    # --------------------
    if score >= 30:
        signal = "STRONG BUY"
    elif score >= 15:
        signal = "BUY"
    elif score <= -30:
        signal = "STRONG SELL"
    elif score <= -15:
        signal = "SELL"
    else:
        signal = "HOLD"

    return {
        "ticker": ticker,
        "signal": signal,
        "score": round(score, 2),
        "news_sentiment": round(news_sentiment, 4),
        "announcement_score": round(announcement_score, 4),
        "social_sentiment": round(social_sentiment, 4)
    }