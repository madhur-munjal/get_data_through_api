from redis import Redis

def get_redis_client() -> Redis:
    return Redis(
        host="localhost",  # or your Redis container IP
        port=6379,
        db=0,
        decode_responses=True  # returns strings instead of bytes
    )