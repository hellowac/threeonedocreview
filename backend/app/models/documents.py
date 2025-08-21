"""文档相关模型"""

from __future__ import annotations

import random
import uuid
from datetime import datetime, timedelta
from typing import Any

from pydantic import computed_field
from sqlalchemy.dialects.mysql.types import MEDIUMTEXT
from sqlalchemy.orm import Mapped, relationship
from sqlmodel import Field, Relationship, SQLModel, UniqueConstraint

from app.models.common import TableBase
from app.models.enums import (
    FileCategory,
    ProjectTypeEnum,
    ReviewStatus,
    SaveType,
    SectionType,
    ThreeoneOtherCategory,
)

# ----------- 临时函数 ---------


def random_review_status() -> str:
    """随机选择审核状态"""

    return random.choice(list(ReviewStatus))


def random_review_percent() -> float:
    """随机生成审核进度"""

    return random.randint(0, 100)


def random_review_begin() -> datetime:
    """随机审核完成时间"""

    return datetime.now() + timedelta(seconds=random.randint(0, 60 * 6))


def random_review_done() -> datetime:
    """随机审核完成时间"""

    return datetime.now() + timedelta(seconds=random.randint(60 * 6, 60 * 60))


# ---------- 工程定义 ------------


class ProjectBase(SQLModel):
    name: str = Field(min_length=1, max_length=255, description="工程名, 唯一")
    type: ProjectTypeEnum = Field(description="工程类型")


class ProjectCreate(ProjectBase):
    """创建项目时需要的字段"""

    iscuser_id: str


class ProjectUpdate(SQLModel):
    """更新项目时需要的字段， 这里只需要更新状态，用于人工复核时更改状态"""

    review_status: ReviewStatus = Field(
        default_factory=random_review_status, description="人工审核通过/不通过."
    )
    audit_feedback: str | None = Field(None, description="不通过(驳回)时的驳回理由")


class Project(TableBase, ProjectBase, table=True):
    """项目表"""

    # name和名称联合唯一
    __table_args__ = (
        UniqueConstraint("name", "type", name="name_type_unique_constraint"),
    )

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    iscuser_id: str = Field(
        description="isc用户ID",
        foreign_key="iscuser.id",
        nullable=False,
        ondelete="CASCADE",
    )

    version: int = Field(default=1, description="版本/提交次数")

    # 项目的审核进度
    review_status: ReviewStatus = Field(
        default=ReviewStatus.UNREVIEWED, description="审核状态"
    )
    review_percent: float = Field(
        default=0, max_items=100, description="审核进度, 0-100之间"
    )
    review_begin_at: datetime | None = Field(default=None, description="审核开始时间")
    review_done_at: datetime | None = Field(default=None, description="审核完成时间")

    # 后面要重置为初始状态，这里是为了好调试和效果
    # review_status: ReviewStatus = Field(
    #     default_factory=random_review_status, description="审核状态"
    # )
    # review_percent: float = Field(
    #     default_factory=random_review_percent,
    #     max_items=100,
    #     description="审核进度, 0-100之间",
    # )
    # review_begin_at: datetime | None = Field(
    #     default_factory=random_review_begin, description="审核开始时间"
    # )
    # review_done_at: datetime | None = Field(
    #     default_factory=random_review_done, description="审核完成时间"
    # )

    # 审核过后的，建议概述
    review_suggestion: str = Field(default="", description="AI/系统审核建议", sa_type=MEDIUMTEXT)

    # 人工复核不通过(驳回)时的驳回意见
    audit_feedback: str | None = Field(default=None, description="驳回意见")

    documents: Mapped[list[Document]] = Relationship(
        cascade_delete=True, sa_relationship=relationship(back_populates="project")
    )
    documentcontents: Mapped[list[DocumentContent]] = Relationship(
        cascade_delete=True, sa_relationship=relationship(back_populates="project")
    )


class ProjectPublic(ProjectBase):
    """接口调用返回的数据结构"""

    id: uuid.UUID
    version: int
    review_status: ReviewStatus
    review_percent: float
    review_begin_at: datetime | None
    review_done_at: datetime | None
    review_suggestion: str
    audit_feedback: str | None
    create_at: datetime
    update_at: datetime
    is_delete: bool

    model_config = {
        "json_encoders": {datetime: lambda v: v.strftime("%Y-%m-%d %H:%M:%S")}
    }  # type: ignore

    @computed_field
    def create_date(self) -> str:
        """创建日期"""

        return self.create_at.strftime("%Y-%m-%d")


class ProjectsPublic(SQLModel):
    """分页返回项目时的数据结构"""

    data: list[ProjectPublic]
    count: int


# ---------- 文档定义 ------------


# 共享属性
class DocumentBase(SQLModel):
    file_name: str = Field(min_length=1, max_length=255, description="文件名")
    file_suffix: str = Field(
        min_length=1, max_length=255, description="文件后缀, 如: pdf, docx"
    )
    file_size: int = Field(description="文件大小, 单位 字节, 比如: 1024")
    file_category: FileCategory = Field(
        min_length=1, max_length=255, description="文件所属分类"
    )
    save_type: SaveType = Field(
        default="local", min_length=1, max_length=255, description="文件保存类型"
    )
    save_path: str = Field(description="文件保存路径")


# 创建文档时需要的属性
class DocumentCreate(DocumentBase):
    pass


# 更新文档时需要的字段
class DocumentUpdate(SQLModel):
    file_category: ThreeoneOtherCategory = Field(description="文件所属分类")


# 数据库模型, 根据类名推断出的数据库表
class Document(TableBase, DocumentBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    iscuser_id: str = Field(
        description="isc用户ID",
        foreign_key="iscuser.id",
        nullable=False,
        ondelete="CASCADE",
    )
    proj_id: uuid.UUID = Field(
        foreign_key="project.id", nullable=False, ondelete="CASCADE"
    )

    # 反射
    project: Project = Relationship(back_populates="documents")

    proj_version: int = Field(
        description="文件对应项目的第几个版本ID, 该版本id 小于等于项目的版本ID"
    )

    # 文档的审核进度
    review_status: ReviewStatus = Field(
        default=ReviewStatus.UNREVIEWED, description="审核状态"
    )
    review_percent: float = Field(
        default=0, max_items=100, description="审核进度, 0-100之间"
    )
    review_begin_at: datetime | None = Field(default=None, description="审核开始时间")
    review_done_at: datetime | None = Field(default=None, description="审核完成时间")

    # 后面要重置为初始状态，这里是为了好调试和效果
    # review_status: ReviewStatus = Field(
    #     default_factory=random_review_status, description="审核状态"
    # )
    # review_percent: float = Field(
    #     default_factory=random_review_percent,
    #     max_items=100,
    #     description="审核进度, 0-100之间",
    # )
    # review_begin_at: datetime | None = Field(
    #     default_factory=random_review_begin, description="审核开始时间"
    # )
    # review_done_at: datetime | None = Field(
    #     default_factory=random_review_done, description="审核完成时间"
    # )

    review_suggestion: str = Field(default="", description="AI/系统审核建议", sa_type=MEDIUMTEXT)

    task_id: uuid.UUID | None = Field(default=None, description="ai审查时的异步任务ID（celery）")

    documentcontents: Mapped[list[DocumentContent]] = Relationship(
        cascade_delete=True, sa_relationship=relationship(back_populates="document")
    )


# 通过 API 返回的属性，id 始终是必需的
class DocumentPublic(DocumentBase):
    id: uuid.UUID
    proj_id: uuid.UUID
    proj_version: int
    review_status: ReviewStatus
    review_percent: float
    review_begin_at: datetime | None
    review_done_at: datetime | None
    review_suggestion: str
    task_id: uuid.UUID | None
    create_at: datetime
    update_at: datetime
    is_delete: bool

    model_config = {
        "json_encoders": {datetime: lambda v: v.strftime("%Y-%m-%d %H:%M:%S")}
    } # type: ignore

    @computed_field
    def file_size_human(self) -> str:
        """
        将整数类型的文件大小（单位：字节）转换为带单位的字符串。

        :param size_in_bytes: 文件大小，单位为字节（int）
        :param decimal_places: 保留的小数位数（int，默认为2）
        :return: 带单位的字符串，如 "1.23 MB"
        """

        size_in_bytes: int = self.file_size
        decimal_places = 2

        # 定义单位列表
        units = ["B", "KB", "MB", "GB", "TB", "PB"]

        # 如果文件大小为0，直接返回 "0 B"
        if size_in_bytes == 0:
            return f"0 {units[0]}"

        # 初始化单位索引
        unit_index = 0

        # 循环除以1024，直到文件大小小于1024或者单位用完
        while size_in_bytes >= 1024 and unit_index < len(units) - 1:
            size_in_bytes /= 1024 # type: ignore
            unit_index += 1

        # 格式化输出，保留指定的小数位数
        return f"{size_in_bytes:.{decimal_places}f} {units[unit_index]}"

    @computed_field
    def proces_percent_human(self) -> str:
        """将0-1之间的百分比转化为带%的字符串"""

        if self.review_percent == 0:
            return "0%"

        return f"{self.review_percent * 100:.{2}}%"


# 返回分页数据时需要的数据模型
class DocumentsPublic(SQLModel):
    data: list[DocumentPublic]
    count: int


# ---------- 文档内容定义 ------------


# 文档内容共享属性
class DocumentContentBase(SQLModel):
    section: SectionType = Field(description="所属节")
    content: str = Field(description="所属节的内容", sa_type=MEDIUMTEXT)
    suggestion: str = Field(description="AI对该节的建议", sa_type=MEDIUMTEXT)


# 创建文档时需要的属性
class DocumentContentCreate(DocumentContentBase):
    pass


# 数据库模型, 根据类名推断出的数据库表
class DocumentContent(TableBase, DocumentContentBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    iscuser_id: str = Field(
        description="isc用户ID",
        foreign_key="iscuser.id",
        nullable=False,
        ondelete="CASCADE",
    )

    # 反射项目
    proj_id: uuid.UUID = Field(
        foreign_key="project.id",
        nullable=False,
        ondelete="CASCADE",
        description="所属项目",
    )

    project: Project = Relationship(back_populates="documentcontents")

    proj_version: int = Field(
        description="文件对应项目的第几个版本ID, 该版本id 小于等于项目的版本ID"
    )

    # 反射文档
    doc_id: uuid.UUID = Field(
        description="所属文档",
        foreign_key="document.id",
        nullable=False,
        ondelete="CASCADE",
    )

    document: Document = Relationship(back_populates="documentcontents")


# 通过 API 返回的属性
class DocumentContentPublic(DocumentContentBase):
    id: uuid.UUID
    proj_id: uuid.UUID
    proj_version: int
    doc_id: uuid.UUID


# ---------- 文档内容审查定义 ----------


class DocumentContentReviewBase(SQLModel):
    """文档内容审查基础类"""


class DocumentContentReview(TableBase, DocumentContentReviewBase, table=True):
    """文档内容审查结果表"""

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    iscuser_id: str = Field(
        description="isc用户ID",
        foreign_key="iscuser.id",
        nullable=False,
        ondelete="CASCADE",
    )

    # 反射项目
    proj_id: uuid.UUID = Field(
        foreign_key="project.id",
        nullable=False,
        ondelete="CASCADE",
        description="所属项目",
    )
    proj_version: int = Field(
        description="文件对应项目的第几个版本ID, 该版本id 小于等于项目的版本ID"
    )

    # 反射文档
    doc_id: uuid.UUID = Field(
        description="所属文档",
        foreign_key="document.id",
        nullable=False,
        ondelete="CASCADE",
    )

    # 反射文档内容
    content_id: uuid.UUID = Field(
        description="所属文档内容",
        foreign_key="documentcontent.id",
        nullable=False,
        ondelete="CASCADE",
    )

    section: SectionType = Field(description="所属节")

    question: str | None = Field(default=None, description="存在的问题描述", sa_type=MEDIUMTEXT)
    question_tag: str | None = Field(default=None, max_length=255, description="问题标签")

    feedback: str | None = Field(
       default=None, description="针对问题的反馈描述", sa_type=MEDIUMTEXT
    )
    feedback_tag: str | None = Field(default=None, max_length=255, description="反馈的标签")

    reference_filename: str | None = Field(default=None, max_length=255, description="参考文件")
    reference_content: str | None = Field(default=None, description="参考内容", sa_type=MEDIUMTEXT)
    reference_location: str | None = Field(default=None, description="引用文件中内容的位置", sa_type=MEDIUMTEXT)

    source_text: str | None = Field(default=None, description="原文内容，简述", sa_type=MEDIUMTEXT)
    source_location: str | None = Field(default=None, description="原文内容位置", sa_type=MEDIUMTEXT)

    ai_error: str | None = Field(
        None, description="审查过程中出现的错误", sa_type=MEDIUMTEXT
    )


class DocumentContentReviewPublic(SQLModel):
    """api接口返回内容"""

    id: uuid.UUID
    proj_id: uuid.UUID
    proj_version: int
    doc_id: uuid.UUID
    content_id: uuid.UUID
    section: SectionType
    question: str | None
    question_tag: str | None
    feedback: str | None
    feedback_tag: str | None
    reference_filename: str | None
    reference_content: str | None
    reference_location: str | None
    source_text: str | None
    source_location: str | None
    ai_error: str | None

    create_at: datetime
    is_delete: bool

    model_config = {
        "json_encoders": {datetime: lambda v: v.strftime("%Y-%m-%d %H:%M:%S")}
    }  # type: ignore


class DocumentContentReviewsPublic(SQLModel):
    data: list[DocumentContentReviewPublic]
    count: int
