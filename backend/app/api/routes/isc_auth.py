"""模拟isc的oss登录模块"""
from datetime import datetime
from typing import Annotated

import requests
from fastapi import APIRouter, Body, HTTPException, Query
from fastapi.responses import RedirectResponse
from loguru import logger

from app.api.deps import RedisDep, SessionDep, cache_userinfo
from app.api.schems import (
    IscLoginPayload,
    IscLoginSuccessResp,
    TicketTokenResp,
    UserinfoResp,
)
from app.core.config import settings
from app.models.iscuser import IscUser


class IscMockOssAuth:

    router = APIRouter(prefix='/isc_sso', tags=['isc'])

    def __init__(self) -> None:
        self.router.get('/logout')(self.logout)
        self.router.get('/login')(self.logout)


    def logout(self, service: Annotated[str, Query(description="服务的部署地址/登录后重定向地址")]) -> RedirectResponse:
        """ 模拟isc登出后，登录成功后的跳转 """

        # 假的ticket
        ticket = 'ST-184134-7ye9d334JffjuvUXqJyE-isc-sso.qh.sgcc.com.cn'

        redirect_url = service + f'?ticket={ticket}'

        return RedirectResponse(redirect_url)

class IscJavaAuth:

    router = APIRouter(prefix='/permission', tags=['isc'])

    def __init__(self) -> None:
        self.router.post('/login', response_model=IscLoginSuccessResp)(self.login)

    def login(self, session: SessionDep, redis: RedisDep, payload: Annotated[IscLoginPayload, Body(description="根据isc oss登录后的ticket获取用户信息")]) -> IscLoginSuccessResp:
        """ 根据用户传入的ticket进行登录

        1. 将tocket 转换为 token
        2. 根据token 获取用户信息，是有过期时间的。
        3. 将用户信息缓存到redis中，用于操作时获取用户信息并存储相关操作的用户ID。
        4. 将用户信息保存到数据库中，如果没有。
        5. 返回用户信息给前端用于显示。
        """

        # 1. 将tocket 转换为 token

        # 'http://20.78.193.180:18080/acloud-isc-token/oauth/token'
        ticket2token_url = settings.isc_ticket2token_url

        # 返回示例
        # {
        #     "access_token": "a3165ffc-a207-4a8f-951e-4b26aa221e0e",
        #     "expires_in": 1800
        # }
        resp = requests.post(ticket2token_url, params=payload.model_dump(mode='json'))

        if resp.status_code != 200:
            logger.info(f"ticket转token失败: [{resp.status_code}] => {resp.text}")
            raise HTTPException(500, f"ticket转token失败: {resp.text}")

        logger.info(f"ticket 数据: {resp.json() = }")

        token_resp = TicketTokenResp.model_validate(resp.json())

        # 2. 根据token 获取用户信息，是有过期时间的。

        # "http://20.78.193.180:18080/acloud-isc-token/users/info"

        userinfo_url = settings.isc_userinfo_url
        authorization_key = f"Bearer {token_resp.access_token}"

        headers = {
            "Authorization": authorization_key,
            "Cookie": f"SESSION={token_resp.access_token}"
        }

        params = {
            "_t": int(datetime.now().timestamp())
        }

        # 返回示例
        # {
        #     "id": "1F4957AA20594E2D8F1E920DFE0CE385",
        #     "username": "lbhai5217",
        #     "name": "李宝海",
        #     "orgId": "8B9669DF65ED55D1E053E31BD70A70E4"
        # }
        uinfo_resp = requests.get(userinfo_url, headers=headers, params=params)

        if uinfo_resp.status_code != 200:
            logger.info(f"获取用户信息失败: {token_resp.access_token} => {resp.text}")
            raise HTTPException(500, f"获取用户信息失败: {token_resp.access_token} => {resp.text}")

        uinfo = UserinfoResp.model_validate(uinfo_resp.json())

        # 3. 将用户信息缓存到redis中，用于操作时获取用户信息并存储相关操作的用户ID。
        expires_in = token_resp.expires_in - 2
        logger.info(f"用户信息过期秒数: {expires_in}")
        cache_userinfo(redis, uinfo, token_resp.access_token, expires_in)

        # 4. 将用户信息保存到数据库中，如果没有。
        iscuser = session.get(IscUser, uinfo.id)
        if not iscuser:
            session.add(IscUser.model_validate(uinfo))
            session.commit()
            logger.info(f"新增iscuser: {uinfo.name} 成功!")

        # 5. 返回用户信息给前端用于显示。
        return IscLoginSuccessResp(jwt=token_resp.access_token, user=uinfo)

isc_mock_oss_router = IscMockOssAuth().router
auth_router = IscJavaAuth().router

