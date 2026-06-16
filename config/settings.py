import os
from dotenv import load_dotenv

load_dotenv(override=True)

DB_URL = os.getenv("DB_URL")

REDIS_HOST = os.getenv("REDIS_HOST")

REDIS_PORT = int(os.getenv("REDIS_PORT"))