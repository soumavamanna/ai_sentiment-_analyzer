# services/technical_score.py

def compute_technical_score(
    market_data,
    sentiment
):

    if not market_data:
        return 1.0

    score = 1.0

    rsi = market_data["rsi_14"]
    volume_ratio = market_data["volume_ratio"]
    volatility = market_data["volatility_20d"]

    if sentiment > 0:

        if rsi < 30:
            score += 0.25

        elif rsi > 70:
            score -= 0.20

    else:

        if rsi > 70:
            score += 0.25

        elif rsi < 30:
            score -= 0.20

    if volume_ratio > 2:

        score += 0.20

    if volatility > 0.08:

        score -= 0.15

    return max(score, 0.5)