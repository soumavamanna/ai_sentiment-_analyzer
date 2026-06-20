# services/signal_fusion.py

def calculate_composite_score(
    sentiment_score: float, 
    event_strength: float, 
    volume_ratio: float, 
    return_20d: float, 
    novelty_score: float, 
    source_credibility: float
) -> int:
    """
    Calculates Phase 3.3 Composite Ranking Score.
    Target Formula: 0.25 sentiment + 0.25 event_strength + 0.20 volume_spike + 
                    0.15 momentum + 0.10 novelty + 0.05 source_quality
    """
    # 1. Normalize momentum to a rough -1.0 to 1.0 scale
    norm_momentum = max(min((return_20d or 0.0) * 10, 1.0), -1.0) 
    
    # 2. Normalize volume (usually ~1.0; a spike is > 2.0)
    norm_volume = min((volume_ratio or 0.0) / 3.0, 1.0) 

    # 3. Apply Roadmap Weights
    weighted_sum = (
        (0.25 * sentiment_score) +
        (0.25 * event_strength) +
        (0.20 * norm_volume) +
        (0.15 * norm_momentum) +
        (0.10 * novelty_score) +
        (0.05 * source_credibility)
    )

    # 4. Scale from raw [-1.0 to 1.0] to a [0 to 100] index score
    composite_index = (weighted_sum + 1) * 50
    
    # Cap strictly between 0 and 100
    return int(max(0, min(100, composite_index)))