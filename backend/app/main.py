from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI
from fastapi.routing import APIRoute
from loguru import logger
from redis import StrictRedis
from redis.connection import ConnectionPool
from starlette.middleware.cors import CORSMiddleware

from app.api.main import api_router
from app.core.config import settings


def custom_generate_unique_id(route: APIRoute) -> str:
    return f"{route.tags[0]}-{route.name}"

@asynccontextmanager # type: ignore
async def lifespan(app: FastAPI) -> Any:
    logger.info("【lifespan】初始化...")

    # 初始化Redis
    redis = StrictRedis.from_pool(ConnectionPool(host=settings.REDIS_HOST, port=settings.REDIS_PORT, password=settings.REDIS_PASS, db=0))
    app.state.redis = redis

    yield

    # 关闭redis
    redis.close()


app = FastAPI(
    title=settings.PROJECT_NAME,
    lifespan=lifespan,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    generate_unique_id_function=custom_generate_unique_id,
)

# Set all CORS enabled origins
if settings.all_cors_origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.all_cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.include_router(api_router, prefix=settings.API_V1_STR)
