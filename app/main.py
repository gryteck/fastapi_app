from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from fastapi_cache.decorator import cache

from redis import asyncio as aioredis

from app.users.router import router as router_users
from app.bookings.router import router as router_bookings
from app.hotels.router import router as router_hotels
from app.pages.router import router as router_pages
from app.images.router import router as router_images


@asynccontextmanager
async def lifespan(app: FastAPI):
    redis = aioredis.from_url('redis://localhost:6379')
    FastAPICache.init(RedisBackend(redis), prefix="cache")
    yield

app = FastAPI(lifespan=lifespan)

app.mount('/static', StaticFiles(directory='app/static'), 'static')

app.include_router(router_users)
app.include_router(router_bookings)
app.include_router(router_hotels)
app.include_router(router_pages)
app.include_router(router_images)
