import base64
import uuid
from io import BytesIO

import pymupdf
import requests
from celery import Task  # type: ignore
from loguru import logger
from pymupdf import Document
from sqlmodel import Session

from app.api.schems import PdfOcrResResponse
from app.api.utils import download_document_from_oss_v1
from app.core import celery_app
from app.core.config import settings
from app.core.db import engine
from app.models.enums import SaveType
from app.mydocx.entry import Extract, RenderFormat
from app.tasks.common import cur_time, review_err, save_docx_shtml_to_db


def pdf2png2text(filepath: str | BytesIO, proj_name: str, proj_version: int) -> tuple[str , str]:
    """ pdf文件转PNG再调用OCR识别出文本，并返回

    参考接口文档:

        1.2 通用ocr识别图片接口: https://kdocs.cn/l/ct7Ln2R98HDz?linkname=KhwyszKB9S
    """

    process_msgs: list[str] = []

    msg = f"项目:【{proj_name}】【第{proj_version}次提交】开始OCR提取PDF文件..."
    process_msgs.append(f"{cur_time()} - {msg}")
    logger.info(msg)

    pdfdoc: Document = pymupdf.open(filepath)

    msg = f"项目:【{proj_name}】【第{proj_version}次提交】PDF文件共有: {review_err(str(len(pdfdoc)))} 页 内容"
    process_msgs.append(f"{cur_time()} - {msg}")
    logger.info(msg)

    lines: list[str] = []

    for pno, page in enumerate(pdfdoc, start=1): # type: ignore
        page_pixmap: pymupdf.Pixmap = page.get_pixmap(matrix=pymupdf.Matrix(2, 2)) # type: ignore

        png_bytes = page_pixmap.tobytes(output='png') # 输出为png的图片

        url = settings.ocr_text_url

        payload = {
            "img_base64": base64.b64encode(png_bytes).decode()
        }

        resp = requests.post(url, json=payload, )

        if resp.status_code != 200:
            msg = f"项目:【{proj_name}】【第{proj_version}次提交】ocr识别pdf文件【第{pno}页】内容失败: {resp.text}"
            process_msgs.append(f"{cur_time()} - {msg}")
            logger.info(msg)
            raise Exception(msg)
            continue

        # res_json = resp.json()

        ocr_res = PdfOcrResResponse.model_validate_json(resp.text)

        if ocr_res.code != 0:
            msg = f"项目:【{proj_name}】【第{proj_version}次提交】ocr识别pdf文件【第{pno}页】内容失败: {ocr_res.msg}"
            process_msgs.append(f"{cur_time()} - {msg}")
            logger.info(msg)
            # raise Exception(msg)
            continue

        for text_block in ocr_res.data.ocr_text.text_blocks:
            lines.append(text_block.rec_text or '')

        # 一页之后添加一个空行。
        lines.append('\n')

    msg = f"项目:【{proj_name}】【第{proj_version}次提交】PDF文件OCR识别内容完成!"
    process_msgs.append(f"{cur_time()} - {msg}")
    logger.info(msg)

    # 使用换行连接每行文本
    pdf_text = '\n'.join(lines)

    return pdf_text, '\n'.join(process_msgs)


@celery_app.task(bind=True)
def audit_scan_pdf(
    self: Task,  # noqa: ARG001
    *,
    proj_id: str,  # uuid.UUID,
    proj_version: int,
    proj_type: str, # noqa: ARG001
    proj_name: str, # noqa: ARG001
    doc_id: str,  # uuid.UUID,
    iscuser_id: str,
    filepath: str,
    _save_type: str,
) -> str | None:

    process_msgs: list[str] = []

    save_type = SaveType(_save_type)

    msg = f"项目:【{proj_name}】【第{proj_version}次提交】开始处理pdf文件..."
    process_msgs.append(f"{cur_time()} - {msg}")
    logger.info(msg)

    # 本地存储
    if save_type == SaveType.LOCAL:

        absolute_filepath: str | BytesIO = str(settings.UPLOAD_FILES_DIR / filepath)

        msg = f"项目:【{proj_name}】【第{proj_version}次提交】本地文件绝对地址: {absolute_filepath}"
        process_msgs.append(f"{cur_time()} - {msg}")
        logger.info(msg)

    # oss 存储
    else:
        absolute_filepath = download_document_from_oss_v1(filepath)

        msg = f"项目:【{proj_name}】【第{proj_version}次提交】OSS存储地址: {filepath}"
        process_msgs.append(f"{cur_time()} - {msg}")
        logger.info(msg)

    with Session(bind=engine) as session:
        pdf_text, _process_msg = pdf2png2text(absolute_filepath, proj_name, proj_version)

        process_msgs.append(_process_msg)

        review_taskid, _process_msg = save_docx_shtml_to_db(
            session,
            proj_name,
            uuid.UUID(proj_id),
            proj_version,
            uuid.UUID(doc_id),
            iscuser_id,
            pdf_text,
        )

        process_msgs.append(_process_msg)


        msg = f"项目:【{proj_name}】【第{proj_version}次提交】保存文件内容完成"
        process_msgs.append(f"{cur_time()} - {msg}")
        logger.info(msg)

    return "\n".join(process_msgs)


@celery_app.task(bind=True)
def audit_docx(
    self: Task,  # noqa: ARG001
    *,
    proj_id: str,  # uuid.UUID,
    proj_version: int,
    proj_type: str, # noqa: ARG001
    proj_name: str, # noqa: ARG001
    doc_id: str,  # uuid.UUID,
    iscuser_id: str,
    filepath: str,
    _save_type: str,
) -> str | None:
    """解析docx的三措文件，保存内容到数据库，并创建agent审查的celery任务，并返回ID"""

    process_msgs: list[str] = []

    save_type = SaveType(_save_type)

    msg = f"项目:【{proj_name}】【第{proj_version}次提交】开始处理docx文件..."
    process_msgs.append(f"{cur_time()} - {msg}")
    logger.info(msg)

    if save_type == SaveType.LOCAL:

        absolute_filepath: str|BytesIO = str(settings.UPLOAD_FILES_DIR / filepath)

        msg = f"项目:【{proj_name}】【第{proj_version}次提交】本地文件绝对地址: {absolute_filepath}"
        process_msgs.append(f"{cur_time()} - {msg}")
        logger.info(msg)

    # oss 存储
    else:
        absolute_filepath = download_document_from_oss_v1(filepath)

        msg = f"项目:【{proj_name}】【第{proj_version}次提交】OSS存储地址: {filepath}"
        process_msgs.append(f"{cur_time()} - {msg}")
        logger.info(msg)

    with Session(bind=engine) as session:

        msg = f"项目:【{proj_name}】【第{proj_version}次提交】开始解析docx文件..."
        process_msgs.append(f"{cur_time()} - {msg}")
        logger.info(msg)

        parser = Extract(absolute_filepath, use_oss=False)
        docx_shtml = parser.parse(render_format=RenderFormat.txt)

        msg = f"项目:【{proj_name}】【第{proj_version}次提交】解析docx文件完成"
        process_msgs.append(f"{cur_time()} - {msg}")
        logger.info(msg)

        review_taskid, _process_msg = save_docx_shtml_to_db(
            session,
            proj_name,
            uuid.UUID(proj_id),
            proj_version,
            uuid.UUID(doc_id),
            iscuser_id,
            docx_shtml,
        )

        process_msgs.append(_process_msg)

        msg = f"项目:【{proj_name}】【第{proj_version}次提交】保存文件内容完成"
        process_msgs.append(f"{cur_time()} - {msg}")
        logger.info(msg)

    return "\n".join(process_msgs)
