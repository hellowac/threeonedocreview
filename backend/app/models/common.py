from datetime import datetime

from sqlmodel import Field, SQLModel


class TableBase(SQLModel):
    create_at: datetime = Field(
        default_factory=datetime.now, description="默认创建时间"
    )
    update_at: datetime = Field(
        default_factory=datetime.now, description="默认更新时间"
    )
    is_delete: bool = Field(default=False, description="是否已删除")


class EnumPair(SQLModel):
    """枚举对"""

    name: str
    value: str
