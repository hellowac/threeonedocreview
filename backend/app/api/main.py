from fastapi import APIRouter
from loguru import logger

from app.api.deps import VerifyIscTokenDep
from app.api.routes import (
    analysis,
    celery_result,
    chat,
    documents,
    isc_auth,
    sys_settings,
    tools,
)
from app.core.config import settings

api_router = APIRouter()

# isc 模拟登录
if settings.ENVIRONMENT != 'prod':
    logger.info("isc oss 模拟登录已启动...")
    api_router.include_router(isc_auth.isc_mock_oss_router)

# isc 的java端校验
api_router.include_router(isc_auth.auth_router)

# 三措文档接口
api_router.include_router(analysis.analysis_router, dependencies=(VerifyIscTokenDep,))
api_router.include_router(
    documents.document_enum_router, dependencies=(VerifyIscTokenDep,)
)
api_router.include_router(documents.projects_router, dependencies=(VerifyIscTokenDep,))
api_router.include_router(documents.documents_router, dependencies=(VerifyIscTokenDep,))
api_router.include_router(
    documents.document_content_router, dependencies=(VerifyIscTokenDep,)
)
api_router.include_router(documents.dc_review_router, dependencies=(VerifyIscTokenDep,))

# 在线解析工具
api_router.include_router(tools.tools_router, dependencies=(VerifyIscTokenDep,))

# celery 结果
api_router.include_router(
    celery_result.celeryresult_router, dependencies=(VerifyIscTokenDep,)
)

# 系统设置
api_router.include_router(sys_settings.router, dependencies=(VerifyIscTokenDep,))

# 智能助手接口
api_router.include_router(chat.chat_session_router)
api_router.include_router(chat.chat_router)
