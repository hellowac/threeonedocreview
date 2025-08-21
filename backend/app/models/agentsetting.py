import uuid
from datetime import datetime

import pytz
from sqlalchemy.dialects.mysql.types import MEDIUMTEXT
from sqlmodel import Field, SQLModel

from app.models.common import TableBase
from app.models.enums import AgentType, ForSection


class AgentSettingBase(SQLModel):
    """智能体设置基础"""

    protocol: str = Field(
        min_length=1, max_length=255, description="接口协议: http/https"
    )
    host: str = Field(min_length=1, max_length=255, description="主机名")
    port: int = Field(description="主机端口")
    app_key: str = Field(min_length=1, max_length=255, description="APP KEY")
    agent_code: str = Field(min_length=1, max_length=255, description="智能体编码")
    agent_version: str = Field(
        min_length=1, max_length=255, description="智能体版本编码"
    )
    is_enable: bool = Field(default=True, description = "是否启用，即审查的智能体是否可用")


class AgentSetting(TableBase, AgentSettingBase, table=True):
    id: uuid.UUID = Field(
        default_factory=uuid.uuid4, primary_key=True, description="主键"
    )
    session_id: str | None = Field(max_length=255, description="会话ID")
    agent_type: AgentType = Field(default=AgentType.assistant, description="该智能体的类型")
    section: ForSection = Field(description="该智能体审查的节")
    desc: str | None = Field(
        default=None, max_length=255, description="该智能体的描述", sa_type=MEDIUMTEXT
    )


class AgentSettingCreate(AgentSetting):
    """创建设置需要的结构"""

    pass


class AgentSettingPublic(AgentSetting):
    """接口返回的智能体配置结构"""

    pass


class AgentSettingsPublic(SQLModel):
    data: list[AgentSettingPublic]
    count: int


# ----------------- agent setting debug payload -----------------


class AgentSettingDebug(SQLModel):
    """agentsetting 调试内容"""

    content: str
    attchement_content: str | None = None
    timeout: float | None = None


# ----------------- agent setting debug payload -----------------


class AgentSettingDebugRecord(TableBase, SQLModel, table=True):
    """agentsetting调试记录表"""

    id: int | None = Field(default=None, primary_key=True, description="主键")

    # ------- 本次请求基本信息
    protocol: str = Field(
        min_length=1, max_length=255, description="接口协议: http/https"
    )
    host: str = Field(min_length=1, max_length=255, description="主机名")
    port: int = Field(description="主机端口")
    app_key: str = Field(min_length=1, max_length=255, description="APP KEY")
    agent_code: str = Field(min_length=1, max_length=255, description="智能体编码")
    agent_version: str = Field(
        min_length=1, max_length=255, description="智能体版本编码"
    )
    session_id: str | None = Field(
        default=None, max_length=255, description="会话ID，实时创建"
    )
    agent_type: AgentType = Field(default=AgentType.assistant, description="该智能体的类型")
    section: ForSection = Field(description="该智能体审核的对应的节")

    # ----- 请求时构造参数
    req_begin_at: datetime = Field(description="请求开始的时间")
    req_url: str | None = Field(
        default=None, max_length=255, description="请求的url地址"
    )
    req_header: str | None = Field(
        default=None, description="请求时的header头", sa_type=MEDIUMTEXT
    )
    req_payload: str | None = Field(
        default=None, description="请求时的json载荷", sa_type=MEDIUMTEXT
    )

    resp_done_at: datetime | None = Field(default=None, description="响应获取的时间")
    resp_status: int | None = Field(
        default=None, description="返回的状态码，比如: 200, 404..."
    )
    resp_spend: float = Field(default=0, description="响应耗时, 单位秒")
    resp_header: str | None = Field(
        default=None, description="响应时的header头", sa_type=MEDIUMTEXT
    )
    resp_text: str | None = Field(
        default=None, description="响应的文本", sa_type=MEDIUMTEXT
    )
    resp_res_text: str | None = Field(
        default=None, description="响应的文本字符串", sa_type=MEDIUMTEXT
    )
    resp_res_json: str | None = Field(
        default=None, description="响应的文本json数据", sa_type=MEDIUMTEXT
    )
    resp_can_validate: bool = Field(
        default=False,
        description="响应的文本，是否可以正常通过 AgentResponseModel 校验",
    )

    # ----- 请求调用发生错误的堆栈
    error_traceback: str | None = Field(
        default=None, description="请求过程中发生错误的堆栈信息", sa_type=MEDIUMTEXT
    )

    model_config = {
        "json_encoders": {datetime: lambda v: v.astimezone(pytz.timezone('Asia/Shanghai')).strftime("%Y-%m-%d %H:%M:%S")}
    }  # type: ignore


class AgentSettingDebugRecordPublic(AgentSettingDebugRecord):
    """接口返回的智能体配置结构"""

    model_config = {
        "json_encoders": {datetime: lambda v: v.astimezone(pytz.timezone('Asia/Shanghai')).strftime("%Y-%m-%d %H:%M:%S")}
    }  # type: ignore


class AgentSettingDebugRecordsPublic(SQLModel):
    data: list[AgentSettingDebugRecordPublic]
    count: int

    model_config = {
        "json_encoders": {datetime: lambda v: v.astimezone(pytz.timezone('Asia/Shanghai')).strftime("%Y-%m-%d %H:%M:%S")}
    }  # type: ignore
