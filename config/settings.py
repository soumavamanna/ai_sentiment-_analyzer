import os
from dotenv import load_dotenv

load_dotenv()

DB_URL = os.getenv(
    "DB_URL"
)

FINNHUB_KEY = os.getenv(
    "FINNHUB_KEY"
)

REDDIT_CLIENT_ID = os.getenv(
    "REDDIT_CLIENT_ID"
)

REDDIT_CLIENT_SECRET = os.getenv(
    "REDDIT_CLIENT_SECRET"
)

REDIS_HOST = os.getenv(
    "REDIS_HOST",
    "localhost"
)

REDIS_PORT = int(
    os.getenv(
        "REDIS_PORT",
        6379
    )
)