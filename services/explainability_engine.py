# services/explainability_engine.py

def generate_explanation(
    ticker: str, 
    score: int, 
    sentiment: str, 
    volume_ratio: float, 
    event_type: str, 
    novelty_score: float
) -> str:
    """Generates a human-readable string explaining the composite score."""
    reasons = []
    
    if event_type and event_type.lower() not in ["none", ""]:
        reasons.append(f"Identified catalyst: {event_type.title()}")
        
    if sentiment.lower() == "positive":
        reasons.append("Bullish news sentiment detected.")
    elif sentiment.lower() == "negative":
        reasons.append("Bearish news sentiment detected.")
        
    # Safety check in case volume_ratio is None or missing
    if volume_ratio and volume_ratio > 1.5:
        reasons.append(f"Unusual volume spike ({round((volume_ratio - 1) * 100)}% above 20d average).")
        
    if novelty_score > 0.8:
        reasons.append("Highly novel catalyst (breaking news).")

    if not reasons:
        reasons.append("Routine market noise / Standard volume.")

    reason_str = "\n- ".join(reasons)
    
    return f"Ticker: {ticker}\nSignal Score: {score}/100\nReasons:\n- {reason_str}"