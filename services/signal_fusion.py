def calculate_signal_strength(
    sentiment_score,
    novelty_score,
    impact_score,
    event_confidence,
    technical_score
):

    return round(

        sentiment_score

        * novelty_score

        * impact_score

        * event_confidence

        * technical_score,

        4
    )