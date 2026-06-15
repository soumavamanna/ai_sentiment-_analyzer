from ingestion.social.reddit_collector import RedditCollector
from ingestion.social.moneycontrol_collector import MoneyControlCollector
import os
from dotenv import load_dotenv
load_dotenv()
class SocialService:

    def __init__(self):
        self.moneycontrol = MoneyControlCollector()

        """ self.reddit = RedditCollector(
            client_id=os.getenv("REDDIT_CLIENT_ID"),
            client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
            user_agent="stockbot"
        )"""

        

    def collect(self):

        data = []

        """ try:
            data.extend(
                self.reddit.fetch_posts()
            )
        except Exception as e:
            print(e)"""

        try:
            data.extend(
                self.moneycontrol.fetch_discussions(
                    "https://mmb.moneycontrol.com"
                )
            )
        except Exception as e:
            print(e)

        return data