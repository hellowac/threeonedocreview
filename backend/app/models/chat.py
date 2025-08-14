"""智能助手, 会话记录模型"""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy.dialects.mysql.types import MEDIUMTEXT
from sqlalchemy.orm import Mapped, relationship
from sqlmodel import Field, Relationship, SQLModel

from app.models.common import TableBase

# --------- 会话表 -----------


class ChatSessionBase(SQLModel):
    title: str = Field(min_length=1, max_length=255, description="会话名称")


# 只支持更新会话名称
class ChatSessionUpdate(SQLModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)  # type: ignore


# 数据库模型, 根据类名推断出的数据库表
class ChatSession(TableBase, ChatSessionBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    iscuser_id: str = Field(
        description="isc用户ID",
        foreign_key="iscuser.id",
        nullable=False,
        ondelete="CASCADE",
    )

    chats: Mapped[list[Chat]] = Relationship(
        cascade_delete=True,
        sa_relationship=relationship(back_populates="session"),
    )


# API返回的数据需要的数据结构
class ChatSessionPublic(SQLModel):
    id: uuid.UUID
    title: str
    create_at: datetime
    update_at: datetime
    is_delete: bool

    model_config = {
        "json_encoders": {datetime: lambda v: v.strftime("%Y-%m-%d %H:%M:%S")}
    } # type: ignore


class ChatSessionsPublic(SQLModel):
    data: list[ChatSessionPublic]
    count: int


# --------- 会话记录表 -----------


# 对话记录共享属性
class ChatBase(SQLModel):
    question: str = Field(description="用户提问", sa_type=MEDIUMTEXT)


# 创建对话记录时需要的属性
class ChatCreate(ChatBase):
    pass


# 创建对话记录时需要的属性
class ChatCreateFromQuestion(SQLModel):
    question: str


# 数据库模型, 根据类名推断出的数据库表
class Chat(TableBase, ChatBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    iscuser_id: str = Field(
        description="isc用户ID",
        foreign_key="iscuser.id",
        nullable=False,
        ondelete="CASCADE",
    )

    session_id: uuid.UUID = Field(
        description="会话ID",
        foreign_key="chatsession.id",
        nullable=False,
        ondelete="CASCADE",
    )

    session: Mapped[ChatSession] = Relationship(
        cascade_delete=True,
        sa_relationship=relationship(back_populates="chats"),
    )

    answer: str = Field(default="", description="助手回答", sa_type=MEDIUMTEXT)
    answer_at: datetime | None = Field(default=None, description="ai回答的时间")


# API返回的数据需要的数据结构
class ChatPublic(ChatBase):
    id: uuid.UUID
    session_id: uuid.UUID
    question: str
    answer: str
    answer_at: datetime | None

    # 通用字段
    create_at: datetime
    update_at: datetime
    is_delete: bool

    model_config = {
        "json_encoders": {datetime: lambda v: v.strftime("%Y-%m-%d %H:%M:%S")}
    } # type: ignore


class ChatsPublic(SQLModel):
    data: list[ChatPublic]
    count: int
