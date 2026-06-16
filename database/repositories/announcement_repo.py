from sqlalchemy import text

from database.db import engine


def save_announcements(
    announcements
):

    query = text("""
    INSERT INTO announcements
    (
        announcement_id,
        exchange,
        symbol,
        subject,
        details,
        timestamp,
        attachment_url
    )
    VALUES
    (
        :announcement_id,
        :exchange,
        :symbol,
        :subject,
        :details,
        :timestamp,
        :attachment_url
    )
    ON CONFLICT (announcement_id)
    DO NOTHING
    """)

    with engine.begin() as conn:

        for announcement in announcements:

            conn.execute(
                query,
                announcement
            )
            