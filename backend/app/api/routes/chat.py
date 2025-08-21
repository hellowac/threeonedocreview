import json
import uuid
from typing import Annotated

from fastapi import (
    APIRouter,
    Body,
    HTTPException,
    Path,
    Query,
)
from loguru import logger
from sqlmodel import Session, asc, col, desc, func, select

from app.api.deps import SessionDep, UserinfoDep
from app.models.agentsetting import AgentSetting

# 文档及内容的模型
from app.models.chat import (
    Chat,
    ChatCreateFromQuestion,
    ChatPublic,
    ChatSession,
    ChatSessionPublic,
    ChatSessionsPublic,
    ChatSessionUpdate,
    ChatsPublic,
)
from app.models.enums import ForSection
from app.tasks.reviews import get_agent_resp_text, post_agent_api

DEFAULT_SESSION_TITLE = "新会话"


class ChatSessionRoute:
    router = APIRouter(prefix="/chats/sessions", tags=["chat session"])

    def __init__(self) -> None:
        self.router.get("/", response_model=ChatSessionsPublic)(self.read_chat_sessions)
        self.router.get("/search", response_model=ChatSessionsPublic)(
            self.search_chat_sessions
        )
        self.router.post("/", response_model=ChatSessionPublic)(
            self.create_chat_session
        )
        self.router.post("/{session_id}/put", response_model=ChatSessionPublic)(
            self.put_chat_session
        )

    def read_chat_sessions(
        self, session: SessionDep, uinfo: UserinfoDep
    ) -> ChatSessionsPublic:
        """获取对话的会话列表"""

        count_statement = select(func.count()).select_from(ChatSession)

        if not uinfo.is_superuser:
            count_statement = count_statement.where(ChatSession.iscuser_id == uinfo.id)

        count = session.exec(count_statement).one()

        statement = select(ChatSession)
        if not uinfo.is_superuser:
            statement = statement.where(ChatSession.iscuser_id == uinfo.id)

        statement = statement.order_by(desc(ChatSession.create_at))  # 按创建时间倒序

        csessions = session.exec(statement).all()

        publics = [ChatSessionPublic.model_validate(csession) for csession in csessions]

        return ChatSessionsPublic(data=publics, count=count)

    def search_chat_sessions(
        self,
        session: SessionDep,
        uinfo: UserinfoDep,
        key: Annotated[str, Query(description="关键字")],
    ) -> ChatSessionsPublic:
        """按关键字搜索会话标题，并返回会话信息"""
        count_statement = (
            select(func.count())
            .select_from(ChatSession)
            .where(col(ChatSession.title).contains(key))
        )
        if not uinfo.is_superuser:
            count_statement = count_statement.where(ChatSession.iscuser_id == uinfo.id)
        count = session.exec(count_statement).one()

        statement = select(ChatSession).where(col(ChatSession.title).contains(key))
        if not uinfo.is_superuser:
            statement = statement.where(ChatSession.iscuser_id == uinfo.id)

        statement = statement.order_by(desc(ChatSession.create_at))  # 按创建时间倒序
        csessions = session.exec(statement).all()

        publics = [ChatSessionPublic.model_validate(csession) for csession in csessions]

        return ChatSessionsPublic(data=publics, count=count)

    def create_chat_session(
        self, session: SessionDep, uinfo: UserinfoDep
    ) -> ChatSessionPublic:
        """新建会话"""

        csession = ChatSession(title=DEFAULT_SESSION_TITLE, iscuser_id=uinfo.id)
        session.add(csession)
        session.commit()
        session.refresh(csession)

        return ChatSessionPublic.model_validate(csession)

    def put_chat_session(
        self,
        session: SessionDep,
        session_id: Annotated[uuid.UUID, Path(description="会话ID")],
        update_in: Annotated[ChatSessionUpdate, Body(description="会话更新的字段")],
    ) -> ChatSessionPublic:
        """更新会话的名称"""

        dsession = session.get(ChatSession, session_id)
        if not dsession:
            raise HTTPException(status_code=404, detail="会话不存在")

        update_dict = update_in.model_dump(exclude_unset=True)
        dsession.sqlmodel_update(update_dict)
        session.add(dsession)
        session.commit()
        session.refresh(dsession)

        return ChatSessionPublic.model_validate(dsession)


chat_session_router = ChatSessionRoute().router


class ChatRoute:
    router = APIRouter(prefix="/{session_id}/chats", tags=["chats"])

    def __init__(self) -> None:
        self.router.get("/", response_model=ChatsPublic)(self.read_chats)
        self.router.post("/", response_model=ChatPublic)(self.create_chat)

    def read_chats(
        self,
        session: SessionDep,
        uinfo: UserinfoDep,
        session_id: Annotated[uuid.UUID, Path(description="会话ID")],
    ) -> ChatsPublic:
        """检索对话记录."""

        count_statement = (
            select(func.count()).select_from(Chat).where(Chat.session_id == session_id)
        )
        if not uinfo.is_superuser:
            count_statement = count_statement.where(Chat.iscuser_id == uinfo.id)

        count = session.exec(count_statement).one()

        statement = select(Chat).where(Chat.session_id == session_id)
        if not uinfo.is_superuser:
            statement = statement.where(Chat.iscuser_id == uinfo.id)

        statement = statement.order_by(asc(Chat.create_at))

        chats = session.exec(statement).all()

        publics = [ChatPublic.model_validate(chat) for chat in chats]

        return ChatsPublic(data=publics, count=count)

    def create_chat(
        self,
        session: SessionDep,
        uinfo: UserinfoDep,
        session_id: Annotated[uuid.UUID, Path(description="会话ID")],
        payload: Annotated[ChatCreateFromQuestion, Body(description="创建的问题")],
    ) -> ChatPublic:
        """创建一个问题（对话记录）"""

        csession = session.get(ChatSession, session_id)

        if not csession:
            raise HTTPException(404, "该会话不存在")

        if csession.title == DEFAULT_SESSION_TITLE:
            csession.title = payload.question
            session.add(csession)
            session.commit()
            session.refresh(csession)

        chat = Chat(
            question=payload.question, session_id=session_id, iscuser_id=uinfo.id
        )
        session.add(chat)
        session.commit()
        session.refresh(chat)

        # todo: 向ai发起提取，等待回答
        # 等待AI回答，但之前应该有提问记录。
        chat.answer = ask_agent(session, payload.question)
        session.add(chat)
        session.commit()
        session.refresh(chat)

        return ChatPublic.model_validate(chat)


def ask_agent(session: Session, question: str) -> str:
    """向AI提问"""

    statement = (
        select(AgentSetting)
        .where(AgentSetting.section == ForSection.assistant)
        .limit(1)
    )
    setting = session.exec(statement).first()

    if not setting:
        raise HTTPException(500, "获取agent参数失败！")

    ai_anwser: str = ''

    ai_anwser, err_msg = get_agent_resp_text(post_agent_api(setting, question, is_chat=True))
    logger.info(f"ai回答: {ai_anwser}")

    if err_msg:
        raise HTTPException(500, err_msg)

    # ["\\n\\n未找到具体支撑材料，暂不做回答。"]
    if ai_anwser.startswith('["') and ai_anwser.endswith(']'):
        ai_anwser = json.loads(ai_anwser)[0]
        ai_anwser = ai_anwser.strip()

    return ai_anwser


chat_router = ChatRoute().router
