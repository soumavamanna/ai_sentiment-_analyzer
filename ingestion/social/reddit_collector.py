import praw

from datetime import datetime

from utils.cache_manager import (
    CacheManager
)


class RedditCollector:

    def __init__(
        self,
        client_id,
        client_secret,
        user_agent
    ):

        self.reddit = praw.Reddit(
            client_id=client_id,
            client_secret=client_secret,
            user_agent=user_agent
        )

    def fetch_posts(self):

        subreddits = [
            "IndianStreetBets",
            "IndiaInvestments"
        ]

        results = []

        for sub in subreddits:

            subreddit = (
                self.reddit.subreddit(
                    sub
                )
            )

            for post in subreddit.hot(
                limit=25
            ):

                item_id = (
                    f"reddit_"
                    f"{post.id}"
                )

                if (
                    CacheManager
                    .is_processed(
                        "reddit",
                        item_id
                    )
                ):
                    continue

                results.append({

                    "post_id":
                        post.id,

                    "platform":
                        "reddit",

                    "author":
                        str(post.author),

                    "title":
                        post.title,

                    "text":
                        post.selftext,

                    "engagement":
                        (
                            post.score
                            +
                            post.num_comments
                        ),

                    "created_at":
                        datetime
                        .fromtimestamp(
                            post.created_utc
                        )
                })

                CacheManager.mark_processed(
                    "reddit",
                    item_id
                )

        return results