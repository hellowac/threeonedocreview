from collections.abc import Generator
from typing import Annotated

from fastapi import Depends, FastAPI, Header, HTTPException, Request
from redis import StrictRedis
from sqlmodel import Session

from app.api.schems import UserinfoResp
from app.core.config import settings
from app.core.db import engine
from app.models.documents import SaveType


def get_db() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session


def get_redis(req: Request) -> StrictRedis:
    """获取redis的strictRedis实例

    该redis的实例在app的lifespan中实例化。
    """

    app: FastAPI = req.app

    return app.state.redis


def get_isc_token(Token: Annotated[str, Header()]) -> str:
    """获取header中的Token的值"""

    if not Token:
        raise HTTPException(status_code=400, detail="Token 头缺失")

    return Token

SessionDep = Annotated[Session, Depends(get_db)]
IscTokenDep = Annotated[str, Depends(get_isc_token)]
VerifyIscTokenDep = Depends(get_isc_token)
RedisDep = Annotated[StrictRedis, Depends(get_redis)]

# ------------ ISC 用户信息逻辑 ------------


def get_userinfo(redis: RedisDep, token: IscTokenDep) -> UserinfoResp | None:
    """获取缓存的已登陆的用户信息"""

    key = f"isc_logined_{token}"

    userinfo_str: str | None = redis.get(key)  # type: ignore

    if not userinfo_str:
        raise HTTPException(401, "需要重新登陆")

    uinfo = UserinfoResp.model_validate_json(userinfo_str)

    # 再延长3分钟
    expire_in = 60 * 3
    cache_userinfo(redis, uinfo, token, expires_in=expire_in)

    return uinfo


def cache_userinfo(
    redis: StrictRedis, userinfo: UserinfoResp, token: str, expires_in: int
) -> bool:
    """缓存用户信息到redis"""

    key = f"isc_logined_{token}"
    userinfo_str = userinfo.model_dump_json()

    # 缓存用户信息
    res: bool = redis.setex(key, expires_in, userinfo_str)  # type: ignore

    return res


UserinfoDep = Annotated[UserinfoResp, Depends(get_userinfo)]

# ------------- 旧的用户校验逻辑 ---------


def get_document_save_type() -> SaveType:
    # if settings.is_local_enviroment:
    #     return SaveType.LOCAL

    # return SaveType.OSS

    return SaveType(settings.FILE_SAVE_TYPE)


SaveTypeDep = Annotated[SaveType, Depends(get_document_save_type)]
