import redis

redis_client = redis.Redis(
    host="localhost",
    port=6379,
    db=0,
    decode_responses=True,

    socket_timeout=5,

    socket_connect_timeout=5,

    health_check_interval=30
)