from sqlalchemy import text

from database.db import engine


def save_articles(
    articles
):

    query = text("""
    INSERT INTO articles
    (
        article_id,
        title,
        content,
        source,
        url,
        published_at
    )
    VALUES
    (
        :article_id,
        :title,
        :content,
        :source,
        :url,
        :published_at
    )
    ON CONFLICT DO NOTHING
    """)

    with engine.begin() as conn:

        for article in articles:

            conn.execute(
                query,
                article
            )