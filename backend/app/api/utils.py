import os
from datetime import datetime
from pathlib import Path

import alibabacloud_oss_v2 as oss
import requests
from fastapi import UploadFile
from loguru import logger

from app.api.schems import (
    ClearSessionPayload,
    ClearSessionResponseModel,
    CreateSessionPayload,
    CreateSessionResponseModel,
)
from app.core.config import settings
from app.models.agentsetting import AgentSetting


def save_document_to_local(uploadfile: UploadFile) -> str:
    upload_dir = settings.UPLOAD_FILES_DIR / datetime.now().strftime("%Y%m%d")
    os.makedirs(upload_dir, exist_ok=True)

    if uploadfile.filename is None:
        raise ValueError("文件名为空")

    filepath = upload_dir / uploadfile.filename

    with open(filepath, "wb") as fw:
        fw.write(uploadfile.file.read())

    # 去掉前缀 + /, 必须加 '/' 否则为绝对地址了。
    relative_filepath = str(filepath).replace(f"{settings.UPLOAD_FILES_DIR}/", "")

    return relative_filepath


def save_document_to_oss(proj_type: str, uploadfile: UploadFile) -> str:
    """上传文档至阿里云OSS存储

    文档参考:

        https://help.aliyun.com/zh/oss/developer-reference/get-started-with-oss-sdk-for-python-v2

        仓库:

        https://github.com/aliyun/alibabacloud-oss-python-sdk-v2/blob/master/README-CN.md
    """
    if uploadfile.filename is None:
        raise ValueError("文件名为空")

    region = settings.OSS_ACCESS_REGION  # "cn-hangzhou"
    bucket_name = settings.OSS_ACCESS_BUCKET  # "your bucket name"

    day = datetime.now().strftime("%Y%M%d")
    object_name = (
        Path(settings.OSS_STORE_PATH) / proj_type / day / uploadfile.filename
    )  # "your object name"

    logger.info(f"上传文件到OSS: {object_name}")

    # 加载凭证
    credentials_provider = oss.credentials.StaticCredentialsProvider(
        settings.OSS_ACCESS_KEY_ID, settings.OSS_ACCESS_KEY_SECRET
    )

    # 使用 SDK 的默认配置
    cfg = oss.config.load_default()
    cfg.credentials_provider = credentials_provider
    cfg.region = region
    cfg.endpoint = settings.OSS_ACCESS_ENDPOINT

    client = oss.Client(cfg)

    result = client.put_object(
        oss.PutObjectRequest(
            bucket=bucket_name,
            key=str(object_name),
            body=uploadfile.file,
        )
    )

    print(f"oss推送文件成功, ETag {result.etag}")

    return str(object_name)


def create_agent_session( agent_setting: AgentSetting) -> str:
    """创建1个session"""

    url = settings.build_agent_create_session_api(agent_setting.protocol, agent_setting.host, agent_setting.port)
    logger.info(f"创建session url: {url}")
    headers = {
        "Authorization": f"Bearer {agent_setting.app_key}",
        "Content-Type": "application/json",
    }
    payload = CreateSessionPayload(
        agentCode=agent_setting.agent_code,
        agentVersion=agent_setting.agent_version,
    ).model_dump(mode="json")

    resp = requests.post(url, json=payload, headers=headers)

    if resp.status_code != 200:
        logger.info(f"获取session失败: {resp.text}")
        raise Exception(f"获取session失败, err: {resp.text}")

    res = CreateSessionResponseModel.model_validate(resp.json())

    return res.data.uniqueCode

def clear_agent_session(agent_setting: AgentSetting, session_id: str | None = None) -> None:
    """调用接口停止已有的session

    session_id: 动态传入的session_id
    """

    url = settings.build_agent_clear_session_api(agent_setting.protocol, agent_setting.host, agent_setting.port)
    logger.info(f"清理session url: {url}")
    headers = {
        "Authorization": f"Bearer {agent_setting.app_key}",
        "Content-Type": "application/json",
    }

    clear_session_id = session_id or agent_setting.session_id

    assert clear_session_id is not None, "session_id 不能为空"

    payload = ClearSessionPayload(sessionId=clear_session_id).model_dump(mode='json')

    resp = requests.post(url, json=payload, headers=headers)

    if resp.status_code != 200:
        raise Exception(f"清理session失败！status_code:{resp.status_code} {resp.text}")

    res = ClearSessionResponseModel.model_validate(resp.json())

    if not res.success:
        raise Exception(f"清理session失败！status_code:{resp.status_code} {resp.text}")

    return None


def delete_agent_session(agent_setting: AgentSetting, session_id: str | None = None) -> None:
    """调用接口删除已有的session

    session_id: 动态传入的session_id
    """

    url = settings.build_agent_delete_session_api(agent_setting.protocol, agent_setting.host, agent_setting.port)
    logger.info(f"删除session url: {url}")
    headers = {
        "Authorization": f"Bearer {agent_setting.app_key}",
        "Content-Type": "application/json",
    }

    delete_session_id = session_id or agent_setting.session_id

    assert delete_session_id is not None, "session_id 不能为空"

    payload = ClearSessionPayload(sessionId=delete_session_id).model_dump(mode='json')

    resp = requests.post(url, json=payload, headers=headers)

    if resp.status_code != 200:
        raise Exception(f"删除session失败！err:{resp.text}")

    res = ClearSessionResponseModel.model_validate(resp.json())

    if not res.success:
        raise Exception(f"删除session失败！err:{resp.text}")

    return None
