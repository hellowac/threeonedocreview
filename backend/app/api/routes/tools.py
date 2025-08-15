import uuid
from typing import Annotated, Any

import html2text
from fastapi import APIRouter, File, HTTPException, Path, Query, UploadFile
from loguru import logger
from sqlmodel import col, desc, func, select

from app.api.deps import SaveTypeDep, SessionDep, UserinfoDep
from app.api.utils import save_document_to_local, save_document_to_oss_v2
from app.models.enums import SaveType

# 文档及内容的模型
from app.models.parsedfile import (
    ParsedFile,
    ParsedFilePublic,
    ParsedFilePublicContent,
    ParsedFilesPublic,
)
from app.mydocx.entry import Extract, RenderFormat


class ToolRoute:
    router = APIRouter(prefix="/tool", tags=["tool"])

    def __init__(self) -> None:
        self.router.get("/parse/files", response_model=ParsedFilesPublic)(
            self.get_parsed_files
        )
        self.router.post("/parse/files", response_model=ParsedFilePublic)(
            self.post_parsed_files
        )
        self.router.get("/parse/files/search", response_model=ParsedFilesPublic)(
            self.search_parsed_files
        )
        self.router.get(
            "/parse/files/{file_id}", response_model=ParsedFilePublicContent
        )(self.get_parsed_file_content)

    def get_parsed_files(
        self, session: SessionDep, uinfo: UserinfoDep
    ) -> ParsedFilesPublic:
        """获取已解析的所有文件"""

        count_statement = (
            select(func.count())
            .select_from(ParsedFile)
            .where(ParsedFile.is_delete == False)  # noqa: E712
        )
        if not uinfo.is_superuser:
            count_statement = count_statement.where(ParsedFile.iscuser_id == uinfo.id)

        count = session.exec(count_statement).one()

        statement = (
            select(ParsedFile).where(ParsedFile.is_delete == False)  # noqa: E712
        )
        if not uinfo.is_superuser:
            statement = statement.where(ParsedFile.iscuser_id == uinfo.id)

        statement = statement.order_by(desc(ParsedFile.create_at))  # noqa: E712
        items = [
            ParsedFilePublic.model_validate(f) for f in session.exec(statement).all()
        ]

        return ParsedFilesPublic(data=items, count=count)

    def post_parsed_files(
        self,
        session: SessionDep,
        uinfo: UserinfoDep,
        save_type: SaveTypeDep,
        docx_file: Annotated[UploadFile, File(description="要解析的docx文件")],
    ) -> Any:
        """上传要解析的文件"""

        # 提取 docx、pdf
        file_suffix = ""
        if docx_file.filename is not None:
            file_suffix = docx_file.filename.rsplit(".")[-1]

        assert docx_file.filename is not None, "文件名不能为空"
        assert docx_file.size is not None, "文件大小不能为空"

        # 保存到本地
        if save_type == SaveType.LOCAL:
            save_path = save_document_to_local(docx_file)
        else:
            save_path = save_document_to_oss_v2("parsedfile", docx_file)

        parsedfile = ParsedFile(
            iscuser_id=uinfo.id,
            file_name=docx_file.filename,
            file_suffix=file_suffix,
            file_size=docx_file.size,
            html_content="",
            md_content="",
            txt_content="",
            save_type=save_type,
            save_path=save_path,
        )

        session.add(parsedfile)
        session.commit()
        session.refresh(parsedfile)

        extracter = Extract(docx_file.file, use_oss=False)
        html_content = extracter.parse(render_format=RenderFormat.shtml)
        md_content = html2text.html2text(html_content)
        txt_content = extracter.parse(render_format=RenderFormat.txt)

        logger.info(f"解析的txt文本: {txt_content = }")

        parsedfile.html_content = html_content
        parsedfile.md_content = md_content
        parsedfile.txt_content = txt_content

        # 更新文档内容
        session.add(parsedfile)
        session.commit()

        return ParsedFilePublic.model_validate(parsedfile)

    def search_parsed_files(
        self,
        session: SessionDep,
        uinfo: UserinfoDep,
        key: Annotated[str, Query(description="搜索的key")],
    ) -> ParsedFilesPublic:
        """搜索已上传并解析的文件"""

        count_statement = (
            select(func.count())
            .select_from(ParsedFile)
            .where(
                ParsedFile.is_delete == False, col(ParsedFile.file_name).contains(key)  # noqa: E712
            )
        )

        if not uinfo.is_superuser:
            count_statement = count_statement.where(ParsedFile.iscuser_id == uinfo.id)

        count = session.exec(count_statement).one()

        statement = (
            select(ParsedFile).where(
                ParsedFile.is_delete == False, col(ParsedFile.file_name).contains(key)  # noqa: E712
            )
        )
        if not uinfo.is_superuser:
            statement = statement.where(ParsedFile.iscuser_id == uinfo.id)

        statement = statement.distinct()

        items = [
            ParsedFilePublic.model_validate(f) for f in session.exec(statement).all()
        ]

        return ParsedFilesPublic(data=items, count=count)

    def get_parsed_file_content(
        self,
        session: SessionDep,
        file_id: Annotated[uuid.UUID, Path(description="文件ID")],
    ) -> ParsedFilePublicContent:
        """获取已上传文件的内容"""

        parsedfile = session.get(ParsedFile, file_id)

        if not parsedfile:
            raise HTTPException(404, "文件不存在")

        return ParsedFilePublicContent.model_validate(parsedfile)


tools_router = ToolRoute().router
