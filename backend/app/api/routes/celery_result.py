from datetime import date, timedelta
from typing import Annotated, Literal

from fastapi import APIRouter, Query
from sqlmodel import desc, func, select

from app.api.deps import SessionDep
from app.core import celery_app

# 文档及内容的模型
from app.models.celery_result import CeleryResult, CeleryResultsPublic


class CeleryResultRoute:
    router = APIRouter(prefix="/celery", tags=["celery result"])

    def __init__(self) -> None:
        self.router.get("/result")(self.get_celery_results)
        self.router.get("/task/names")(self.get_task_names)

    def get_celery_results(
        self,
        session: SessionDep,
        name: Annotated[str | None, Query(description="任务名")] = None,
        start_date: Annotated[
            date | None, Query(description="开始日期,如: 2025-05-12")
        ] = None,
        end_date: Annotated[
            date | None, Query(description="结束日期,如: 2025-06-14")
        ] = None,
        status: Annotated[
            Literal["PENDING", "SUCCESS", "FAILURE"] | None,
            Query(description="审核状态"),
        ] = None,
        skip: Annotated[int, Query()] = 0,
        limit: Annotated[int, Query()] = 10,
    ) -> CeleryResultsPublic:
        """获取celery结果"""

        where_statement = []

        if name:
            where_statement.append(CeleryResult.name == name)

        if start_date:
            where_statement.append(CeleryResult.date_done >= start_date)  # type: ignore

        if end_date:
            # <= date 转换为 < (date+1day)
            where_statement.append(
                CeleryResult.date_done < (end_date + timedelta(days=1))  # type: ignore
            )

        if status:
            where_statement.append(CeleryResult.status == status)  # type: ignore

        count = session.exec(
            select(func.count()).select_from(CeleryResult).where(*where_statement)
        ).one()

        statement = (
            select(CeleryResult)
            .where(*where_statement)
            .order_by(desc(CeleryResult.id))
            .offset(skip)
            .limit(limit)
        )

        # results = [CeleryResultPublic.model_validate(res) for res in session.exec(statement).all()]
        results = list(session.exec(statement).all())

        return CeleryResultsPublic(data=results, count=count)

    def get_task_names(self, session: SessionDep) -> list[str]:
        """获取所有celery的所有任务名称"""

        task_names: list[str] = list(celery_app.tasks.keys())

        task_names = [name for name in task_names if not name.startswith('celery')]

        return task_names


celeryresult_router = CeleryResultRoute().router
