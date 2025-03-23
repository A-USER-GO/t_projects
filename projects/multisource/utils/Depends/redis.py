from aioredis import Redis

from multisource.utils.current_app import get_current_app


async def get_redis() -> Redis:
    app = get_current_app()
    return app.redis