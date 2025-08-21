import traceback
import uuid
from datetime import datetime
from typing import Annotated, Any

import html2text
import pytz
from fastapi import APIRouter, File, Form, HTTPException, Path, Query, UploadFile
from loguru import logger
from sqlmodel import col, desc, func, select

from app.api.deps import SaveTypeDep, SessionDep, UserinfoDep
from app.api.utils import save_document_to_local, save_document_to_oss_v1
from app.core.config import settings
from app.core.enums import OcrApiType
from app.models.enums import SaveType

# 文档及内容的模型
from app.models.parsedfile import (
    ParsedFile,
    ParsedFilePublic,
    ParsedFilePublicContent,
    ParsedFilesPublic,
)
from app.mydocx.entry import Extract, RenderFormat
from app.tasks.audit import ocr_pdf2png2text


class ToolRoute:
    router = APIRouter(prefix="/tool", tags=["tool"])

    def __init__(self) -> None:
        self.router.get("/parse/files")(self.get_parsed_files)
        self.router.post("/parse/files")(self.post_parsed_files)
        self.router.get("/parse/files/search")(self.search_parsed_files)
        self.router.get("/parse/files/{file_id}")(self.get_parsed_file_content)

        # ocr调试
        self.router.post("/ocr/debug")(self.post_ocr_debug)

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
            save_path = save_document_to_oss_v1("parsedfile", docx_file)

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
                ParsedFile.is_delete == False,  # noqa: E712
                col(ParsedFile.file_name).contains(key),
            )
        )

        if not uinfo.is_superuser:
            count_statement = count_statement.where(ParsedFile.iscuser_id == uinfo.id)

        count = session.exec(count_statement).one()

        statement = select(ParsedFile).where(
            ParsedFile.is_delete == False,  # noqa: E712
            col(ParsedFile.file_name).contains(key),
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

    def post_ocr_debug(
        self,
        session: SessionDep,
        api_type: Annotated[OcrApiType, Form(description="ocr调用的接口类型")],
        doc_file: Annotated[UploadFile, File(description="ocr要识别处理的文件")],
    ) -> dict:
        """在线调试ocr识别功能"""

        logger.info(f"ocr调试要使用的类型: {api_type.value}")
        logger.info(f"ocr调试要识别的文件: {doc_file}")

        status_code = 200
        resp_text: str = ""  # "这是原始结果"
        resp_res_text: str = ""  # "这是解析后的结果"
        error_traceback: str | None = None  # "这是来自服务器的错误结果"
        process_msg: str = ""  # "这是处理过程消息"

        req_begin_at = datetime.now(tz=pytz.timezone("Asia/Shanghai"))

        try:
            resp_text, process_msg = ocr_pdf2png2text(
                doc_file.file, proj_name="ocrdebug", proj_version=1, api_type=api_type
            )
            resp_res_text = resp_text

            # resp_text = "这是原始结果"
            # resp_res_text = "这是解析后的结果"
            # error_traceback = None # "这是来自服务器的错误结果"
            # process_msg = "这是处理过程消息"

        except Exception as e:
            logger.exception(e)
            error_traceback = traceback.format_exc()

        configinfo: dict[str, str] = {}

        if api_type == OcrApiType.BAIDU:
            # 获取会话路径
            configinfo["session_path"] = settings.baiduocr_conversation_url
            # 上传文件路径
            configinfo["upload_path"] = settings.baiduocr_upload_url
            # 运行agent路径（执行ocr识别）
            configinfo["agent_path"] = settings.baiduocr_run_url
            # 应用id
            configinfo["app_id"] = settings.BAIDUOCR_APP_ID
            # 项目id
            configinfo["department_id"] = settings.BAIDUOCR_DEPARTMENDD_ID

        else:
            configinfo["session_path"] = settings.ppocr_text_url
            configinfo["upload_path"] = settings.ppocr_text_url
            configinfo["agent_path"] = settings.ppocr_text_url
            configinfo["app_id"] = ""
            configinfo["department_id"] = ""

        resp_done_at = datetime.now(tz=pytz.timezone("Asia/Shanghai"))
        resp_spend = round((resp_done_at - req_begin_at).total_seconds(), 2)

        return {
            "configinfo": configinfo,
            "status_code": status_code,
            "req_begin_at": req_begin_at.strftime('%Y-%m-%d %H:%M:%S'),
            "resp_done_at": resp_done_at.strftime('%Y-%m-%d %H:%M:%S'),
            "resp_spend": resp_spend,
            "resp_text": resp_text,
            "resp_res_text": resp_res_text,
            "error_traceback": error_traceback,
            "process_msg": process_msg,
        }


tools_router = ToolRoute().router
