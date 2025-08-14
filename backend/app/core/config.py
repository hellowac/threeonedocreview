import os
import secrets
import warnings
from pathlib import Path
from typing import Annotated, Any, Literal, Self, cast

from loguru import logger
from pydantic import (
    AnyUrl,
    BeforeValidator,
    EmailStr,
    HttpUrl,
    MySQLDsn,
    computed_field,
    model_validator,
)
from pydantic_core import MultiHostUrl
from pydantic_settings import BaseSettings, SettingsConfigDict

# 与app同级的目录
PROJECT_PATH = Path(__file__).parent.parent


def parse_cors(v: Any) -> list[str] | str:
    if isinstance(v, str) and not v.startswith("["):
        return [i.strip() for i in v.split(",")]
    elif isinstance(v, list | str):
        return v
    raise ValueError(v)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        # Use top level .env file
        env_file=".env",
        env_ignore_empty=True,
        extra="ignore",
    )

    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = secrets.token_urlsafe(32)

    # 本地文件上传目录
    UPLOAD_FILES_DIR: Path = PROJECT_PATH / "uploads"

    FILE_SAVE_TYPE: Literal["oss", "local"] = "local"

    # OSS配置
    OSS_ACCESS_REGION: str = ""
    OSS_ACCESS_KEY_ID: str = ""
    OSS_ACCESS_KEY_SECRET: str = ""
    OSS_ACCESS_BUCKET: str = ""
    OSS_ACCESS_ENDPOINT: str = ""
    OSS_STORE_PATH: str = ""

    # 60 minutes * 24 hours * 8 days = 8 days
    FRONTEND_HOST: str = "http://localhost:5173"
    ENVIRONMENT: Literal["local", "test", "prod"] = "local"

    BACKEND_CORS_ORIGINS: Annotated[
        list[AnyUrl] | str, BeforeValidator(parse_cors)
    ] = []

    PROJECT_NAME: str

    MYSQL_SERVER: str
    MYSQL_PORT: int = 3306
    MYSQL_USER: str
    MYSQL_PASSWORD: str = ""
    MYSQL_DB: str = ""
    MYSQL_DRIVER: str = "mysql"

    # redis 消息队列配置
    REDIS_HOST: str = '127.0.0.1'
    REDIS_PORT: int = 6379
    REDIS_PASS: str = ''
    REDIS_DB: int = 2

    # agent 各个路由的定义
    AGENT_PATH: str = '/xlm-gateway-bo-ihi/sfm-api-gateway/gateway/agent/api/run'
    AGENT_CREAT_SESSION_PATH: str = '/xlm-gateway-bo-ihi/sfm-api-gateway/gateway/agent/api/createSession'
    AGENT_CLEAR_SESSION_PATH: str = '/xlm-gateway-bo-ihi/sfm-api-gateway/gateway/agent/api/clearSession'
    AGENT_DELETE_SESSION_PATH: str = '/xlm-gateway-bo-ihi/sfm-api-gateway/gateway/agent/api/deleteSession'

    # isc auth 的接口定义
    ISC_AUTH_HOST: str = '127.0.0.1'
    ISC_AUTH_PORT: int = 8003
    ISC_AUTH_TOKEN_PATH: str = '/acloud-isc-token/oauth/token'
    ISC_AUTH_USERINFO_PATH: str = '/acloud-isc-token/users/info'

    # ocr 调用接口的定义
    OCR_PROTOCOL: str = 'http'
    OCR_HOST: str = '183.221.0.158'
    OCR_PORT: int = 29966
    OCR_PATH: str = '/api/ocr/text_rec'

    # 超级用户的用户名
    SUPERUSER_USERNAME: str = "lbhai5217"

    @computed_field  # type: ignore[prop-decorator]
    @property
    def isc_ticket2token_url(self) -> str:
        """ isc ticket转token的url """

        return f"http://{self.ISC_AUTH_HOST}:{self.ISC_AUTH_PORT}{self.ISC_AUTH_TOKEN_PATH}"

    @computed_field  # type: ignore[prop-decorator]
    @property
    def isc_userinfo_url(self) -> str:
        """ isc 获取用户信息的url """

        return f"http://{self.ISC_AUTH_HOST}:{self.ISC_AUTH_PORT}{self.ISC_AUTH_USERINFO_PATH}"

    @computed_field  # type: ignore[prop-decorator]
    @property
    def ocr_text_url(self) -> str:
        """ ocr 识别文本，调用URL """

        return f"{self.OCR_PROTOCOL}://{self.OCR_HOST}:{self.OCR_PORT}{self.OCR_PATH}"

    def build_agent_create_session_api(self, protocol: str, host: str, port: int) -> str:
        """ 智能体创建session的链接地址 """

        # post 方法
        port_str = '' if port == 80 else f':{port}'
        return f"{protocol}://{host}{ port_str }{self.AGENT_CREAT_SESSION_PATH}"

    def build_agent_api(self, protocol: str, host: str, port: int) -> str:
        """ 智能体使用session的链接地址 """

        if protocol not in ('http', 'https'):
            raise ValueError(f"不支持http/https以外的协议: {protocol}")

        # post 方法
        port_str = '' if port == 80 else f':{port}'
        return f"{protocol}://{host}{ port_str }{self.AGENT_PATH}"

    def build_agent_clear_session_api(self, protocol: str, host: str, port: int) -> str:
        """ 智能体停止session的链接地址 """

        # post 方法
        port_str = '' if port == 80 else f':{port}'
        return f"{protocol}://{host}{ port_str }{self.AGENT_CLEAR_SESSION_PATH}"

    def build_agent_delete_session_api(self, protocol: str, host: str, port: int) -> str:
        """ 智能体删除session的链接地址 """

        # post 方法
        port_str = '' if port == 80 else f':{port}'
        return f"{protocol}://{host}{ port_str }{self.AGENT_DELETE_SESSION_PATH}"

    @computed_field  # type: ignore[prop-decorator]
    @property
    def all_cors_origins(self) -> list[str]:
        return [str(origin).rstrip("/") for origin in self.BACKEND_CORS_ORIGINS] + [
            self.FRONTEND_HOST
        ]

    @computed_field  # type: ignore[prop-decorator]
    @property
    def SQLALCHEMY_DATABASE_URI(self) -> MySQLDsn:
        uri = MultiHostUrl.build(
            scheme="mysql+mysqlconnector",
            username=self.MYSQL_USER,
            password=self.MYSQL_PASSWORD,
            host=self.MYSQL_SERVER,
            port=self.MYSQL_PORT,
            path=self.MYSQL_DB,
            query="charset=utf8mb4",
        )

        logger.info(f"mysql 数据库地址{uri = }")

        return cast(MySQLDsn, uri)

    @property
    def celery_broker_url(self) -> str:
        """celery broker 链接地址"""

        # broker_url = f"amqp://{self.AMQP_USER}:{self.AMQP_PASS}@{self.AMQP_HOST}:{self.AMQP_PORT}/{self.AMQP_VHOST}"

        if self.REDIS_PASS:
            broker_url = f"redis://:{self.REDIS_PASS}@{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
        else:
            broker_url = f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"

        return broker_url

    @property
    def celery_backend_url(self) -> str:
        """celery backend 链接地址"""

        uri = MultiHostUrl.build(
            scheme="db+mysql",
            username=self.MYSQL_USER,
            password=self.MYSQL_PASSWORD,
            host=self.MYSQL_SERVER,
            port=self.MYSQL_PORT,
            path=self.MYSQL_DB,
            query="charset=utf8mb4",
        )

        logger.info(f"celery backend地址:{uri}")

        return str(uri)

    @computed_field  # type: ignore[prop-decorator]
    @property
    def is_local_enviroment(self) -> bool:
        return self.ENVIRONMENT == "local"

    @model_validator(mode="after")
    def _enforce_oss_seted(self) -> Self:
        if self.FILE_SAVE_TYPE == "oss":
            if not all(
                (
                    self.OSS_ACCESS_BUCKET,
                    self.OSS_ACCESS_ENDPOINT,
                    self.OSS_ACCESS_KEY_ID,
                    self.OSS_ACCESS_KEY_SECRET,
                )
            ):
                raise ValueError("缺少OSS配置")

        return self


settings = Settings()  # type: ignore

os.makedirs(settings.UPLOAD_FILES_DIR, exist_ok=True)
