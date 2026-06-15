from sqlalchemy import text

from database.db import engine


def save_social_posts(
    posts
):

    query = text("""
    INSERT INTO social_posts
    (
        post_id,
        platform,
        author,
        text,
        timestamp,
        engagement
    )
    VALUES
    (
        :post_id,
        :platform,
        :author,
        :text,
        :timestamp,
        :engagement
    )
    ON CONFLICT DO NOTHING
    """)

    with engine.begin() as conn:

        for post in posts:

            conn.execute(
                query,
                post
            )