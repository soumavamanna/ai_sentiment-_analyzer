from database.repositories.company_signal_repo import (
    get_company_context
)


def generate_company_signal(
    ticker: str
):

    ctx = get_company_context(
        ticker
    )

    if not ctx:
        return None

    score = 0

    # --------------------
    # NEWS
    # --------------------

    score += (
        ctx["news_sentiment"] * 30
    )

    # --------------------
    # ANNOUNCEMENTS
    # --------------------

    score += (
        ctx["announcement_score"] * 25
    )

    # --------------------
    # SOCIAL
    # --------------------

    score += (
        ctx["social_sentiment"] * 15
    )

    # --------------------
    # PRICE MOMENTUM
    # --------------------

    score += (
        ctx["return_5d"] * 100 * 0.10
    )

    score += (
        ctx["return_20d"] * 100 * 0.05
    )

    # --------------------
    # RSI
    # --------------------

    rsi = ctx["rsi_14"]

    if rsi < 30:

        score += 10

    elif rsi > 70:

        score -= 10

    # --------------------
    # VOLUME CONFIRMATION
    # --------------------

    if ctx["volume_ratio"] > 2:

        score += 5

    # --------------------
    # VOLATILITY PENALTY
    # --------------------

    if ctx["volatility_20d"] > 0.08:

        score -= 5

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
        "news_sentiment": ctx["news_sentiment"],
        "announcement_score": ctx["announcement_score"],
        "social_sentiment": ctx["social_sentiment"]
    }