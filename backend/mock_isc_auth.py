from typing import Annotated

from fastapi import APIRouter, Depends, FastAPI, Header, Query
from loguru import logger

from app.api.schems import TicketTokenResp, UserinfoResp

app = FastAPI()


# -------------- 注入依赖 --------------


def get_auth_dep(
    Authorization: Annotated[str, Header()], Cookie: Annotated[str, Header()]
) -> str:
    """获取header头中的验证码"""

    logger.info(f"{Authorization = }, { Cookie = }")

    app_key = Authorization.replace("Bearer ", "")

    return app_key


AuthDep = Annotated[str, Depends(get_auth_dep)]


# ---------------------路由函数定义----------------------------

router = APIRouter(prefix="/acloud-isc-token")


@router.post("/oauth/token")
def ticket2token(
    ticket: Annotated[str, Query(description="票据")],
    service: Annotated[str, Query(description="项目地址")],
) -> TicketTokenResp:
    logger.info(f"ticket 2 token: {ticket = } {service = }")

    return TicketTokenResp(
        access_token="a3165ffc-a207-4a8f-951e-4b26aa221e0e", expires_in=1800
    )


@router.get("/users/info")
def userinfo(auth: AuthDep) -> UserinfoResp:


    return UserinfoResp(id="1F4957AA20594E2D8F1E920DFE0CE385", username="lbhai5217", name="李宝海", orgId="8B9669DF65ED55D1E053E31BD70A70E4")


app.include_router(router)
