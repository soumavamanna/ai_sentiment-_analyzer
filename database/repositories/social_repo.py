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


def get_unprocessed_social_posts():
    """Fetches recent social posts that haven't been scored by the NLP engine yet."""
    # We check financial_signals to see if the post_id already exists there
    query = text("""
    SELECT post_id, platform, author, text, timestamp, engagement
    FROM social_posts
    WHERE post_id NOT IN (
        SELECT article_id FROM financial_signals WHERE article_id IS NOT NULL
    )
    AND timestamp >= NOW() - INTERVAL '3 days'
    """)

    with engine.connect() as conn:
        results = conn.execute(query).mappings().fetchall()

    return [dict(row) for row in results]