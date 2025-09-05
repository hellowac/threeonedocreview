from datetime import date, datetime, timedelta
from enum import StrEnum
from typing import Annotated, Literal

from fastapi import (
    APIRouter,
    Query,
)
from sqlmodel import Session, func, select

from app.api.deps import SessionDep
from app.api.schems import (
    AnalysisBarChartData,
    AnalysisOverviewTotal,
    AnalysisPieChartData,
    BarCurPrevData,
    PieChartItem,
    PieCurPrevData,
    QuestionSuggestionChartData,
)

# 文档及内容的模型
from app.models.documents import (
    Document,
    DocumentContentReview,
    Project,
)
from app.models.enums import ReviewStatus


class OverviewTimeType(StrEnum):
    ALL = "all"
    DAY = "day"
    MONTH = "month"
    YEAR = "year"


class AnalysisRoute:
    router = APIRouter(prefix="/analysis", tags=["analysis"])

    def __init__(self) -> None:
        self.router.get("/overview")(self.get_overview_data)
        self.router.get("/question")(self.get_question_data)
        self.router.get("/suggestion")(self.get_suggestion_data)

    def get_overview_data(
        self,
        session: SessionDep,
        time_type: Annotated[OverviewTimeType, Query(description="统计的时间维度")],
    ) -> tuple[AnalysisOverviewTotal, ...]:
        """系统概览统计

        支持按多个时间维度统计4个总量：

        - 工程总量
        - 文档总数
        - 等待审查 (工程数)
        - 审查完毕 (工程数)
        """

        # 工程总量
        proj_total = self.get_proj_total(session, time_type)

        # 文档总数
        doc_total = self.get_doc_total(session, time_type)

        # 等待审查
        unreviewd_proj_total = self.get_proj_total(
            session, time_type, ReviewStatus.UNREVIEWED
        )

        # 审查完毕
        passed_proj_total = self.get_proj_total(
            session, time_type, ReviewStatus.HUMAN_REVIEW_PASSED
        )

        return (proj_total, doc_total, unreviewd_proj_total, passed_proj_total)

    def get_doc_total(
        self, session: Session, time_type: OverviewTimeType
    ) -> AnalysisOverviewTotal:
        """获取文档总量"""

        overview_total = AnalysisOverviewTotal(
            title="文档总量",
            total=0,
            prevTotal=0,
            iconClass="el-icon-document",
            iconColor="#009900",
            isUp=False,
            amplitude="0%",
        )

        statebase = (
            select(func.count())
            .select_from(Document)
            .where(Document.is_delete == False)  # noqa: E712
        )

        if time_type == OverviewTimeType.ALL:
            statement = statebase
            cur_total = session.exec(statement).one()

            prev_total = 0

        else:
            cur_date, prev_date = get_cur_prev_date(time_type)

            assert cur_date is not None
            assert prev_date is not None

            cur_total_statement = statebase.where(Document.create_at >= cur_date)
            cur_total = session.exec(cur_total_statement).one()

            prev_total_statement = statebase.where(
                cur_date > Document.create_at,
                Document.create_at >= prev_date,
            )
            prev_total = session.exec(prev_total_statement).one()

        overview_total.total = cur_total
        overview_total.prevTotal = prev_total
        overview_total.isUp = cur_total > prev_total

        # 计算百分比

        if prev_total:
            overview_total.amplitude = (
                f"{round(abs(cur_total - prev_total) / prev_total, 2) * 100}%"
            )
        else:
            overview_total.amplitude = "100%"

        return overview_total

    def get_proj_total(
        self,
        session: Session,
        time_type: OverviewTimeType,
        review_status: ReviewStatus | None = None,
    ) -> AnalysisOverviewTotal:
        """获取等待审查总量"""

        filter_date_field = Project.create_at

        if review_status is None:
            overview_total = AnalysisOverviewTotal(
                title="工程总量",
                total=0,
                prevTotal=0,
                iconClass="el-icon-folder-opened",
                iconColor="#0066CC",
                isUp=False,
                amplitude="0%",
            )

        elif review_status == ReviewStatus.UNREVIEWED:
            overview_total = AnalysisOverviewTotal(
                title="等待审查",
                total=0,
                prevTotal=0,
                iconClass="el-icon-remove-outline",
                iconColor="#FF9999",
                isUp=False,
                amplitude="0%",
            )
            filter_date_field = Project.review_begin_at  # type: ignore
        else:
            overview_total = AnalysisOverviewTotal(
                title="审查完毕",
                total=0,
                prevTotal=0,
                iconClass="el-icon-circle-check",
                iconColor="#006600",
                isUp=False,
                amplitude="0%",
            )
            filter_date_field = Project.review_done_at  # type: ignore

        # 构造基础的where过滤语句
        statebase = (
            select(func.count())
            .select_from(Project)
            .where(
                Project.is_delete == False  # noqa: E712
            )
        )

        if review_status is not None:
            statebase = statebase.where(Project.review_status == review_status)

        # 根据不同日期类型，构造不同的当前值和上一个日期的值。
        if time_type == OverviewTimeType.ALL:
            statement = statebase
            cur_total = session.exec(statement).one()

            prev_total = 0

        else:
            cur_date, prev_date = get_cur_prev_date(time_type)

            assert cur_date is not None
            assert prev_date is not None

            cur_total_statement = statebase.where(filter_date_field >= cur_date)  # type: ignore
            cur_total = session.exec(cur_total_statement).one()

            prev_total_statement = statebase.where(
                cur_date > filter_date_field,  # type: ignore
                filter_date_field >= prev_date,  # type: ignore
            )
            prev_total = session.exec(prev_total_statement).one()

        overview_total.total = cur_total
        overview_total.prevTotal = prev_total
        overview_total.isUp = cur_total > prev_total

        if prev_total:
            overview_total.amplitude = (
                f"{round(abs(cur_total - prev_total) / prev_total, 2) * 100}%"
            )
        else:
            overview_total.amplitude = "100%"

        return overview_total

    def get_question_data(
        self,
        session: SessionDep,
        time_type: Annotated[OverviewTimeType, Query(description="统计的时间维度")],
    ) -> QuestionSuggestionChartData:
        return self.get_qs_total(session, "question", time_type)

    def get_suggestion_data(
        self,
        session: SessionDep,
        time_type: Annotated[OverviewTimeType, Query(description="统计的时间维度")],
    ) -> QuestionSuggestionChartData:
        _bardata = AnalysisBarChartData(categoryData=[], chartdata=[])

        return self.get_qs_total(session, "suggestion", time_type)

    def get_qs_total(
        self,
        session: Session,
        _from: Literal["question", "suggestion"],
        time_type: OverviewTimeType,
    ) -> QuestionSuggestionChartData:
        field = DocumentContentReview.feedback_tag

        if _from == "question":
            field = DocumentContentReview.question_tag

        statebase = (
            select(field, func.count().label("value"))
            .select_from(DocumentContentReview)
            .where(DocumentContentReview.is_delete == False)  # noqa: E712
        )

        if _from == "question":
            statebase.where(DocumentContentReview.question_tag is not None)

        if _from == "suggestion":
            statebase.where(DocumentContentReview.feedback_tag is not None)

        if time_type == OverviewTimeType.ALL:
            cur_statement = prev_statement = statebase.group_by(field)

        else:
            cur_date, prev_date = get_cur_prev_date(time_type)

            assert cur_date is not None
            assert prev_date is not None

            cur_statement = statebase.where(
                DocumentContentReview.create_at >= cur_date
            ).group_by(field)
            prev_statement = statebase.where(
                cur_date > DocumentContentReview.create_at,
                DocumentContentReview.create_at >= prev_date,
            ).group_by(field)

        cur_res = session.exec(cur_statement).all()
        prev_res = session.exec(prev_statement).all()

        # ----------

        cur_pie_data: list[PieChartItem] = []
        cur_bar_category: list[str] = []
        cur_bar_chardata: list[float] = []

        for item in cur_res:
            if item[0] is None:
                continue

            cur_pie_data.append(PieChartItem(name=item[0], value=item[1]))
            cur_bar_category.append(item[0])
            cur_bar_chardata.append(item[1])

        # --------

        prev_pie_data: list[PieChartItem] = []
        prev_bar_category: list[str] = []
        prev_bar_chardata: list[float] = []

        for item in prev_res:
            if item[0] is None:
                continue

            prev_pie_data.append(PieChartItem(name=item[0], value=item[1]))
            prev_bar_category.append(item[0])
            prev_bar_chardata.append(item[1])

        # --------

        cur_pie = AnalysisPieChartData(cur_pie_data)
        prev_pie = AnalysisPieChartData(prev_pie_data)

        cur_bar = AnalysisBarChartData(
            categoryData=cur_bar_category, chartdata=cur_bar_chardata
        )
        prev_bar = AnalysisBarChartData(
            categoryData=prev_bar_category, chartdata=prev_bar_chardata
        )

        # --------

        if time_type == OverviewTimeType.ALL:
            all_pie = cur_pie
            all_bar = cur_bar
        else:
            all_pie = AnalysisPieChartData([])
            all_bar = AnalysisBarChartData(categoryData=[], chartdata=[])

        pie_curprev_data = PieCurPrevData(all=all_pie, cur=cur_pie, prev=prev_pie)
        bar_curPrev_data = BarCurPrevData(all=all_bar, cur=cur_bar, prev=prev_bar)

        return QuestionSuggestionChartData(
            pieData=pie_curprev_data, barData=bar_curPrev_data
        )


def get_cur_prev_date(time_type: OverviewTimeType) -> tuple[date | None, date | None]:
    """根据不同日期类型，获取当前和上一个日期

    按日为单位:

        今天，昨天

    按月为单位:

        当月，上一个月，这里会考虑当月为1月时的情况，此时上一月为上一年的的12月

    按年为单位:

        今年，上一年
    """

    cur_date, prev_date = None, None

    now = datetime.now()

    if time_type == OverviewTimeType.DAY:
        cur_date = now.date()
        prev_date = (now - timedelta(days=1)).date()

    elif time_type == OverviewTimeType.MONTH:
        cur_date = datetime(year=now.year, month=now.month, day=1)

        if now.month == 1:
            prev_date = datetime(year=(now.year - 1), month=12, day=1)
        else:
            prev_date = datetime(year=now.year, month=now.month, day=1)

    elif time_type == OverviewTimeType.YEAR:
        cur_date = datetime(year=now.year, month=1, day=1)
        prev_date = (now - timedelta(days=1)).date()

    return cur_date, prev_date


analysis_router = AnalysisRoute().router
