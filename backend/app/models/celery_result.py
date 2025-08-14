import json
import pickle
from datetime import datetime
from typing import Any

import pytz
from pydantic import computed_field
from sqlalchemy.types import TypeDecorator
from sqlmodel import Column, Field, LargeBinary, SQLModel, Text


class PickleType(TypeDecorator):
    impl = LargeBinary
    cache_ok = True  # SQLAlchemy 1.4+ 推荐设置

    def process_bind_param(self, value: Any, dialect: Any) -> Any:
        if value is None:
            return None
        return pickle.dumps(value)

    def process_result_value(self, value: Any, dialect: Any) -> Any:
        if value is None:
            return None
        return pickle.loads(value)


class CeleryResult(SQLModel, table=True):
    __tablename__ = "celery_taskmeta"  # type: ignore  # noqa: B015, F821

    id: int | None = Field(None, primary_key=True)  # 自增主键
    task_id: str | None = Field(None, max_length=155, unique=True)
    status: str | None = Field(None, max_length=50)
    # result: bytes = Field(sa_column=Column(LargeBinary))
    result: object = Field(sa_column=Column(PickleType))
    date_done: datetime | None = Field(None)  # 数据库查出来是不带时区的utc时间。
    traceback: str | None = Field(sa_type=Text)
    name: str | None = Field(None, max_length=155)
    args: bytes = Field(sa_column=Column(LargeBinary))
    kwargs: bytes = Field(sa_column=Column(LargeBinary))
    worker: str | None = Field(None, max_length=155)
    retries: int | None = Field(None)
    queue: str | None = Field(None, max_length=155)

    @computed_field
    def kwargs_obj(self) -> dict:
        return json.loads(self.kwargs)

    @computed_field
    def done_at(self) -> str:
        if self.date_done:
            return (
                pytz.utc.localize(self.date_done)
                .astimezone(pytz.timezone("Asia/Shanghai"))
                .strftime("%Y-%m-%d %H:%M:%S")
            )
        return ""


class CeleryResultsPublic(SQLModel):
    data: list[CeleryResult]
    count: int
