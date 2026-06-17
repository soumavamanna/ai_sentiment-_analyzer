EVENT_WEIGHTS = {

    "earnings beat": 1.0,
    "earnings miss": -1.0,

    "guidance raise": 0.9,
    "guidance cut": -0.9,

    "share buyback": 0.8,

    "merger": 0.6,
    "acquisition": 0.6,

    "analyst upgrade": 0.5,
    "analyst downgrade": -0.5,

    "lawsuit": -0.7,

    "ceo departure": -0.4
}

def compute_impact(event_type, confidence):

    weight = EVENT_WEIGHTS.get(
        event_type,
        0
    )

    return round(
        weight * confidence,
        4
    )