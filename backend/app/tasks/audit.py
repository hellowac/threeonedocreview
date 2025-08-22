import base64
import json
import traceback
import uuid
from io import BytesIO
from pathlib import Path
from typing import BinaryIO

import pymupdf
import requests
from celery import Task  # type: ignore
from loguru import logger
from pymupdf import Document
from sqlmodel import Session

from app.api.const import MEDIA_TYPE_MAP
from app.api.schems import PdfOcrResResponse
from app.api.utils import download_document_from_oss_v1
from app.core import celery_app
from app.core.config import settings
from app.core.db import engine
from app.core.enums import OcrApiType
from app.models.enums import SaveType, SectionType
from app.mydocx.entry import Extract, RenderFormat
from app.tasks.common import (
    cur_time,
    save_document_content,
    save_docx_shtml_to_db,
)


def ppocr_post_png(
    proj_name: str, proj_version: int, pno: int, png_bytes: bytes
) -> tuple[str, str]:
    """推送图片bytes到ppocr, 并获取图片里面的文本"""

    process_msgs: list[str] = []

    url = settings.ppocr_text_url

    payload = {"img_base64": base64.b64encode(png_bytes).decode()}

    resp = requests.post(
        url,
        json=payload,
    )

    if resp.status_code != 200:
        msg = f"项目:【{proj_name}】【第{proj_version}次提交】ocr识别pdf文件【第{pno}页】内容失败: {resp.text}"
        process_msgs.append(f"{cur_time()} - {msg}")
        logger.info(msg)

    # res_json = resp.json()

    ocr_res = PdfOcrResResponse.model_validate_json(resp.text)

    if ocr_res.code != 0:
        msg = f"项目:【{proj_name}】【第{proj_version}次提交】ocr识别pdf文件【第{pno}页】内容失败: {ocr_res.msg}"
        process_msgs.append(f"{cur_time()} - {msg}")
        logger.info(msg)

    lines: list[str] = []

    for text_block in ocr_res.data.ocr_text.text_blocks:
        lines.append(text_block.rec_text or "")

    return "\n".join(lines), "\n".join(process_msgs)


def baiduocr_post_png(
    filename: str, file_bytes: bytes, media_type: str, timeout: int|None = None
) -> tuple[str, str]:
    """百度ocr调用api"""

    # 执行过程的消息
    process_msgs: list[str] = []

    # 1. 获取conversation_id

    # 1.1 构造获取conversation_id的请求
    payload = {
        "app_id": settings.BAIDUOCR_APP_ID,
        "department_id": settings.BAIDUOCR_DEPARTMENDD_ID,
    }

    headers = {
        "Authorization": f"Bearer {settings.BAIDUOCR_AUTH}",
        "X-Authorization": f"Bearer {settings.BAIDUOCR_AUTH}",
        "Content-Type": "application/json",
    }

    conversation_id_resp = requests.post(
        settings.baiduocr_conversation_url, json=payload, headers=headers
    )

    # 1.2 响应示例
    # {
    #     "request_id": "afcfc9b0-22ed-4e95-851c-1672257a54e4",
    #     "conversation_id": "724c9124-38f8-4789-947c-5412e59dfb95",
    # }
    _msg = f"【baiduocr】获取conversation_id 响应文本: {conversation_id_resp.text}"
    process_msgs.append(_msg)
    logger.info(_msg)

    if conversation_id_resp.status_code != 200:
        err_msg = f"【baiduocr】获取conversation_id失败: {conversation_id_resp.status_code = }"
        logger.info(err_msg)
        process_msgs.append(err_msg)

        return "", "\n".join(process_msgs)

    conversation_id: str = conversation_id_resp.json().get("conversation_id")

    if not conversation_id:
        err_msg = f"【baiduocr】获取conversation_id失败: {conversation_id = }"
        logger.info(err_msg)
        process_msgs.append(err_msg)

        return "", "\n".join(process_msgs)

    # 2. 构造上传文件的请求

    # 2.1 构造上传文件的参数

    # 其他字段，不要与文件放在files中。。
    upload_headers = {
        "Authorization": f"Bearer {settings.BAIDUOCR_AUTH}",
        "X-Authorization": f"Bearer {settings.BAIDUOCR_AUTH}"
    }
    upload_payload = {
        "app_id": settings.BAIDUOCR_APP_ID,
        "department_id": settings.BAIDUOCR_DEPARTMENDD_ID,
        "conversation_id": conversation_id,
    }
    upload_files = {"file": (filename, BytesIO(file_bytes), media_type)}

    _msg = f"【baiduocr】文件 【{filename}】的媒体类型为: {media_type}"
    process_msgs.append(_msg)
    logger.info(_msg)

    # 这里需要是 www-formdata 的格式。
    upload_file_resp = requests.post(
        settings.baiduocr_upload_url,
        data=upload_payload,
        files=upload_files,
        headers=upload_headers,  # 这里不要有content-type字段的值。
    )

    # 示例响应结构
    # {
    #     "request_id": "8b8e65dd-65af-4057-a4cb-d05b7ca857a7",
    #     "id": "69a9305e-ac13-4f8f-a84e-14e56b1caa31",  # 文件ID
    #     "conversation_id": "724c9124-38f8-4789-947c-5412e59dfb95",
    # }
    _msg = f"【baiduocr】获取上传文件响应文本: {upload_file_resp.text}"
    logger.info(_msg)
    process_msgs.append(_msg)

    if upload_file_resp.status_code != 200:
        err_msg = f"【baiduocr】上传文件失败: {upload_file_resp.status_code = }"
        logger.info(err_msg)
        process_msgs.append(err_msg)

        return "", "\n".join(process_msgs)

    uploaded_file_id: str = upload_file_resp.json().get("id")

    if not uploaded_file_id:
        err_msg = f"【baiduocr】获取上传文件的ID失败: {uploaded_file_id = }"
        logger.info(err_msg)
        process_msgs.append(err_msg)

        return "", "\n".join(process_msgs)

    # 3. 根据文件ID获取ocr识别结果。

    # 3.1 构造获取ocr结果的参数
    ocr_res_pyaload = {
        "app_id": settings.BAIDUOCR_APP_ID,
        "department_id": settings.BAIDUOCR_DEPARTMENDD_ID,
        "query": "文件内容是什么",  # 这一句，没有实际作用，主要query是必传参数。(自定义的ocr智能体里面不会使用这个)
        "stream": False,
        "conversation_id": conversation_id,
        "file_ids": [
            uploaded_file_id
        ],  # 根据接口文档，目前智能体里面只解析第一个文件ID。传多了也没用。
    }

    # 此处根据文件大小，需要等待的时长不一，但一般不超过1分钟。
    ocr_res_resp = requests.post(
        settings.baiduocr_run_url, json=ocr_res_pyaload, headers=headers, timeout=timeout
    )

    # 示例响应结构
    # 参考 baiduocr_res.json 文件

    _msg = f"【baiduocr】获取ocr文件识别结果响应文本: {ocr_res_resp.text}"
    logger.info(f"{_msg[:100]}...")
    process_msgs.append(f"{_msg[:100]}...") # 太大的话返回存储到数据库有问题。

    if ocr_res_resp.status_code != 200:
        err_msg = f"【baiduocr】获取ocr文件识别结果失败: {ocr_res_resp.status_code = }"
        logger.info(err_msg)
        process_msgs.append(err_msg)

        return "", "\n".join(process_msgs)

    try:
        ocr_res: dict = ocr_res_resp.json()

        ocr_answer_str: str | None = ocr_res.get("answer")

        # ocr 结果示例参考 baiduocr_res.json 文件
        assert ocr_answer_str is not None, "ocr 识别结果为的answer为None"

        ocr_res = json.loads(json.loads(ocr_answer_str)["output"])

        # 获取段落节点列表
        para_node_tree: list[dict] = ocr_res["para_node_tree"]
        lines: list[str] = []

        for para_node in para_node_tree:
            # 已知段落类型（para_type）有：
            # {'head_tail', 'text', 'root', 'table', 'contents', 'title_1', 'figure', 'title_3', 'title_2', 'title_5', 'title_4', 'title_7', 'title_6'}
            # 排除掉页眉页脚，根节点
            if para_node["para_type"] not in ("head_tail", "root"):
                lines.append(para_node["text"])

        all_text = "\n\n".join(lines)

        return all_text, "\n".join(process_msgs)

    except Exception as e:
        err_msg = f"【baiduocr】解析ocr文件识别结果失败: {e}"
        logger.exception(err_msg)
        process_msgs.append(err_msg)
        process_msgs.append(traceback.format_exc())

    return "", "\n".join(process_msgs)


def ocr_pdf2png2text(
    filename: str,
    filepath: str | BytesIO | BinaryIO,
    proj_name: str,
    proj_version: int,
    *,
    api_type: OcrApiType = OcrApiType.PPOCR,
    timeout: int | None = None
) -> tuple[str, str]:
    """pdf文件转PNG再调用OCR识别出文本，并返回

    参考接口文档:

        1.2 通用ocr识别图片接口: https://kdocs.cn/l/ct7Ln2R98HDz?linkname=KhwyszKB9S
    """

    process_msgs: list[str] = []

    msg = f"项目:【{proj_name}】【第{proj_version}次提交】开始OCR提取PDF文件..."
    process_msgs.append(f"{cur_time()} - {msg}")
    logger.info(msg)

    # 本地ppocr只支持单张图片。
    if api_type == OcrApiType.PPOCR:
        if isinstance(filepath, str):
            pdfdoc: Document = pymupdf.open(filepath)
        else:
            pdfdoc = pymupdf.Document(stream=filepath.read())

        msg = f"项目:【{proj_name}】【第{proj_version}次提交】PDF文件共有: 【{len(pdfdoc)}】 页 内容"
        process_msgs.append(f"{cur_time()} - {msg}")
        logger.info(msg)

        lines: list[str] = []

        for pno, page in enumerate(pdfdoc, start=1):  # type: ignore
            page_pixmap: pymupdf.Pixmap = page.get_pixmap(matrix=pymupdf.Matrix(2, 2))  # type: ignore

            png_bytes = page_pixmap.tobytes(output="png")  # 输出为png的图片

            # 本地 ppocr 识别
            png_text, process_msg = ppocr_post_png(
                proj_name, proj_version, pno, png_bytes
            )

            lines.append(png_text)
            process_msgs.append(process_msg)

            # 一页之后添加一个空行。
            lines.append("\n")

        msg = f"项目:【{proj_name}】【第{proj_version}次提交】PDF文件OCR识别内容完成!"
        process_msgs.append(f"{cur_time()} - {msg}")
        logger.info(msg)

        # 使用换行连接每行文本
        pdf_text = "\n".join(lines)

    # 百度 ocr接口 识别, 支持整个文件
    else:
        if isinstance(filepath, str):
            with open(filepath, "rb") as fr:
                file_bytes = fr.read()
        else:
            file_bytes = filepath.read()

        _suffix = Path(filename).suffix[1:]
        file_media_type = MEDIA_TYPE_MAP.get(_suffix.lower())  # 转为小写后再获取

        assert file_media_type is not None, f"【{filename}】的媒体类型获取失败"

        pdf_text, process_msg = baiduocr_post_png(filename, file_bytes, file_media_type, timeout=timeout)
        process_msgs.append(process_msg)

    return pdf_text, "\n".join(process_msgs)


@celery_app.task(bind=True)
def audit_scan_pdf(
    self: Task,  # noqa: ARG001
    *,
    proj_id: str,  # uuid.UUID,
    proj_version: int,
    proj_type: str,  # noqa: ARG001
    proj_name: str,  # noqa: ARG001
    doc_id: str,  # uuid.UUID,
    iscuser_id: str,
    filepath: str,
    _save_type: str,
    appendix_files: list[dict],  # 附件信息
) -> str | None:
    process_msgs: list[str] = []

    save_type = SaveType(_save_type)

    msg = f"项目:【{proj_name}】【第{proj_version}次提交】开始处理pdf文件..."
    process_msgs.append(f"{cur_time()} - {msg}")
    logger.info(msg)

    # 处理附件
    for appendix_file_info in appendix_files:
        # 立即执行
        process_msg = ocr_appendix_file(
            **appendix_file_info
        )  # 这里的参数定义参考 调用本函数的地方。
        process_msgs.append(process_msg)

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

    # 处理三措文档
    with Session(bind=engine) as session:
        filename = Path(filepath).name

        # 审核的是偶，api类型使用系统设置的。
        pdf_text, _process_msg = ocr_pdf2png2text(
            filename, absolute_filepath, proj_name, proj_version, api_type=settings.OCR_API_TYPE
        )

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
    proj_type: str,  # noqa: ARG001
    proj_name: str,  # noqa: ARG001
    doc_id: str,  # uuid.UUID,
    iscuser_id: str,
    filepath: str,
    _save_type: str,
    appendix_files: list[dict],  # 附件信息
) -> str | None:
    """解析docx的三措文件，保存内容到数据库，并创建agent审查的celery任务，并返回ID"""

    process_msgs: list[str] = []

    save_type = SaveType(_save_type)

    msg = f"项目:【{proj_name}】【第{proj_version}次提交】开始处理docx文件..."
    process_msgs.append(f"{cur_time()} - {msg}")
    logger.info(msg)

    # 处理附件
    for appendix_file_info in appendix_files:
        # 立即执行
        process_msg = ocr_appendix_file(
            **appendix_file_info
        )  # 这里的参数定义参考 调用本函数的地方。
        process_msgs.append(process_msg)

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

    # 处理三措文档
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


@celery_app.task(bind=True)
def ocr_appendix_file(
    self: Task,  # noqa: ARG001
    *,
    proj_id: str,  # uuid.UUID,
    proj_version: int,
    proj_type: str,  # noqa: ARG001
    proj_name: str,  # noqa: ARG001
    doc_id: str,  # uuid.UUID,
    iscuser_id: str,
    filepath: str,
    _save_type: str,
) -> str:
    """解析附件为文本，利用ocr工具

    1. 先从本地或oss拿去文件/图片内容
    2. 根据文件后缀，判断不同的文件类型
    3. 如果是docx，直接解析
    4. 如果是pdf，或图片，根据ocr接口配置，调用不同的接口，识别文件内容，
    5. 保存文件内容到数据库。
    """

    process_msgs: list[str] = []

    save_type = SaveType(_save_type)

    msg = (
        f"【{proj_type}】项目:【{proj_name}】【第{proj_version}次提交】开始处理附件..."
    )
    process_msgs.append(f"{cur_time()} - {msg}")
    logger.info(msg)

    if save_type == SaveType.LOCAL:
        absolute_filepath: str | BytesIO = str(settings.UPLOAD_FILES_DIR / filepath)

        msg = f"【{proj_type}】项目:【{proj_name}】【第{proj_version}次提交】本地文件绝对地址: {absolute_filepath}"
        process_msgs.append(f"{cur_time()} - {msg}")
        logger.info(msg)

    # oss 存储
    else:
        absolute_filepath = download_document_from_oss_v1(filepath)

        msg = f"【{proj_type}】项目:【{proj_name}】【第{proj_version}次提交】OSS存储地址: {filepath}"
        process_msgs.append(f"{cur_time()} - {msg}")
        logger.info(msg)

    with Session(bind=engine) as session:
        msg = f"【{proj_type}】项目:【{proj_name}】【第{proj_version}次提交】开始解析附件..."
        process_msgs.append(f"{cur_time()} - {msg}")
        logger.info(msg)

        # ocr api 类型
        api_type = settings.OCR_API_TYPE

        # 按docx文件处理
        if filepath.endswith(".docx"):
            parser = Extract(absolute_filepath, use_oss=False)
            file_content = parser.parse(render_format=RenderFormat.txt)

        # 按pdf文件处理
        elif filepath.endswith(".pdf"):
            filename = Path(filepath).name
            file_content, _process_msg = ocr_pdf2png2text(
                filename, absolute_filepath, proj_name, proj_version, api_type=api_type
            )

            process_msgs.append(_process_msg)

        # 按图片处理
        else:
            if isinstance(absolute_filepath, BytesIO):
                png_bytes = absolute_filepath.read()

            else:
                with open(absolute_filepath, "rb") as fr:
                    png_bytes = fr.read()

            # 本地ppocr
            pno = 1
            if api_type == OcrApiType.PPOCR:
                file_content, _process_msg = ppocr_post_png(
                    proj_name, proj_version, pno, png_bytes
                )

            # 百度api接口进行ocr
            else:
                filename = Path(filepath).name

                _suffix = Path(filename).suffix[1:]
                file_media_type = MEDIA_TYPE_MAP.get(_suffix.lower())

                assert file_media_type is not None, f"【{filename}】的媒体类型获取失败"

                file_content, _process_msg = baiduocr_post_png(
                    filename, png_bytes, file_media_type
                )

        msg = (
            f"【{proj_type}】项目:【{proj_name}】【第{proj_version}次提交】解析附件完成"
        )
        process_msgs.append(f"{cur_time()} - {msg}")
        logger.info(msg)

        dc = save_document_content(
            session,
            uuid.UUID(proj_id),
            proj_version,
            uuid.UUID(doc_id),
            iscuser_id,
            SectionType.all,
            file_content,
        )

        msg = f"【{proj_type}】项目:【{proj_name}】【第{proj_version}次提交】文件内容ID:{dc.id}"
        process_msgs.append(f"{cur_time()} - {msg}")

        msg = f"【{proj_type}】项目:【{proj_name}】【第{proj_version}次提交】保存文件内容完成"
        process_msgs.append(f"{cur_time()} - {msg}")
        logger.info(msg)

    return "\n".join(process_msgs)
