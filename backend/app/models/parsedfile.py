import uuid
from datetime import datetime

from sqlalchemy.dialects.mysql import MEDIUMTEXT
from sqlmodel import Field, SQLModel

from app.models.common import TableBase
from app.models.enums import SaveType


class ParsedFileBase(TableBase):
    """解析的文件基础"""

    file_name: str = Field(min_length=1, max_length=255, description="文件名")
    file_suffix: str = Field(
        min_length=1, max_length=255, description="文件后缀, 如: pdf, docx"
    )
    file_size: int = Field(description="文件大小, 单位 字节, 比如: 1024")
    save_type: SaveType = Field(
        default="local", min_length=1, max_length=255, description="文件保存类型"
    )
    save_path: str = Field(description="文件保存路径")


class ParsedFileCreate(ParsedFileBase):
    pass


class ParsedFile(ParsedFileBase, table=True):
    """创建文件"""

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, description="文件ID")
    iscuser_id: str = Field(
        description="isc用户ID",
        foreign_key="iscuser.id",
        nullable=False,
        ondelete="CASCADE",
    )
    html_content: str = Field("", description="解析后的html格式的文件内容", sa_type=MEDIUMTEXT)
    md_content: str = Field("", description="解析后的md格式的文件内容", sa_type=MEDIUMTEXT)
    txt_content: str = Field("", description="解析后的txt格式的文件内容", sa_type=MEDIUMTEXT)


class ParsedFilePublic(ParsedFileBase):
    """公开的文件结构"""

    id: uuid.UUID
    # content: str

    model_config = {
        "json_encoders": {datetime: lambda v: v.strftime("%Y-%m-%d %H:%M:%S")}
    }  # type: ignore


class ParsedFilePublicContent(SQLModel):
    """ 已解析的文件内容，html/md格式 """

    html_content: str
    md_content: str
    txt_content: str

class ParsedFilesPublic(SQLModel):
    """文件集合的返回数据类型"""

    data: list[ParsedFilePublic]
    count: int
