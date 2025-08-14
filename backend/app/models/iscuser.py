from __future__ import annotations

from datetime import datetime

from sqlmodel import Field, SQLModel

from app.models.common import TableBase

# --------- ISC用户表 -----------


class IscUserBase(SQLModel):
    """ 创建Isc用户的基本字段 """
    pass


class IscUserUpdate(SQLModel):
    """ 暂不支持更新 """
    pass


class IscUser(TableBase, IscUserBase, table=True):
    id: str = Field(primary_key=True, description="用户User唯一ID")
    username: str = Field(description="用户登录名（纯ascii字母/数字）")
    name: str = Field(description="用户显示名称")
    orgId: str = Field(description="组织ID")


# API返回的数据需要的数据结构
class IscUserPublic(SQLModel):
    id: str
    username: str
    name: str
    orgId: str
    create_at: datetime
    update_at: datetime
    is_delete: bool

    model_config = {
        "json_encoders": {datetime: lambda v: v.strftime("%Y-%m-%d %H:%M:%S")}
    } # type: ignore


class IscUsersPublic(SQLModel):
    data: list[IscUserPublic]
    count: int
