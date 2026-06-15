import requests

from bs4 import BeautifulSoup

from utils.cache_manager import (
    CacheManager
)


class MoneyControlCollector:

    def fetch_discussions(
        self,
        url
    ):

        response = requests.get(
            url,
            timeout=15,
            headers={
                "User-Agent":
                    "Mozilla/5.0"
            }
        )

        soup = BeautifulSoup(
            response.text,
            "html.parser"
        )

        discussions = []

        posts = soup.select(
            ".comment"
        )

        for post in posts[:50]:

            text = (
                post.get_text(
                    strip=True
                )
            )

            item_id = (
                CacheManager
                .generate_hash(
                    text
                )
            )

            if (
                CacheManager
                .is_processed(
                    "moneycontrol",
                    item_id
                )
            ):
                continue

            discussions.append({

                "discussion_id":
                    item_id,

                "source":
                    "moneycontrol",

                "text":
                    text
            })

            CacheManager.mark_processed(
                "moneycontrol",
                item_id
            )

        return discussions