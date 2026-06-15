import hashlib

from infrastructure.cache.redis_client import (
    redis_client
)


class CacheManager:

    @staticmethod
    def generate_hash(text):

        return hashlib.sha256(
            text.encode()
        ).hexdigest()

    @staticmethod
    def is_processed(
        source,
        item_id
    ):

        key = (
            f"{source}:{item_id}"
        )

        return redis_client.exists(
            key
        )

    @staticmethod
    def mark_processed(
        source,
        item_id,
        ttl=604800
    ):

        key = (
            f"{source}:{item_id}"
        )

        redis_client.setex(
            key,
            ttl,
            1
        )

    @staticmethod
    def get_last_timestamp(
        source
    ):

        return redis_client.get(
            f"{source}:last_ts"
        )

    @staticmethod
    def set_last_timestamp(
        source,
        timestamp
    ):

        redis_client.set(
            f"{source}:last_ts",
            timestamp
        )