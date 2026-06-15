from datetime import datetime
from zoneinfo import ZoneInfo


IST = ZoneInfo(
    "Asia/Kolkata"
)


def now_ist():

    return datetime.now(
        IST
    )


def unix_to_ist(
    timestamp
):

    return datetime.fromtimestamp(
        timestamp,
        tz=IST
    )


def utc_to_ist(
    dt
):

    return dt.astimezone(
        IST
    )