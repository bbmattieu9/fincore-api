from fastapi import HTTPException
from time import time

# In-memory store (for now)
request_count = {}

RATE_LIMIT = 5   # max requests
WINDOW = 60      # seconds


def rate_limiter(user_id: int):
    now = time()

    if user_id not in request_count:
        request_count[user_id] = []

    # Remove expired requests
    request_count[user_id] = [
        t for t in request_count[user_id]
        if now - t < WINDOW
    ]

    if len(request_count[user_id]) >= RATE_LIMIT:
        raise HTTPException(
            status_code=429,
            detail="Too many requests"
        )

    request_count[user_id].append(now)