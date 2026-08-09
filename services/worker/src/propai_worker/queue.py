"""Redis queue wiring. One place that knows the queue names."""

from __future__ import annotations

from redis import Redis
from rq import Queue

from propai_core.config import get_settings

DEFAULT_QUEUE = "default"


def redis_connection() -> Redis:
    return Redis.from_url(str(get_settings().redis_url))


def get_queue(name: str = DEFAULT_QUEUE) -> Queue:
    return Queue(name, connection=redis_connection())
