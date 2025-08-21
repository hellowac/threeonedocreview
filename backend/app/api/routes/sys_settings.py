import json
import traceback
import uuid
from datetime import datetime
from typing import Annotated

import pytz
from fastapi import APIRouter, Body, HTTPException, Path, Query
from loguru import logger
from sqlmodel import Session, asc, desc, func, select

from app.api.deps import SessionDep
from app.api.schems import AgentResponseModel
from app.api.utils import (
    clear_agent_session,
    create_agent_session,
    delete_agent_session,
)
from app.models.agentsetting import (
    AgentSetting,
    AgentSettingBase,
    AgentSettingDebug,
    AgentSettingDebugRecord,
    AgentSettingDebugRecordPublic,
    AgentSettingDebugRecordsPublic,
    AgentSettingPublic,
    AgentSettingsPublic,
)
from app.models.enums import AgentType
from app.tasks.reviews import (
    get_agent_resp_text,
    parse_agent_raw_rasp,
    post_agent_api_core,
)


class AgentSettingRoute:
    router = APIRouter(prefix="/agentsettings", tags=["sys settings"])

    def __init__(self) -> None:
        self.router.get("")(self.get_agent_settings)
        self.router.get("/{proj_type}")(self.get_agent_settings_by_type)
        self.router.post("/{setting_id}/update")(self.update_agent_setting)
        self.router.post("/{setting_id}/debug")(self.debug_agent_setting)
        self.router.get("/debug/records")(self.get_debug_records)
        self.router.post("/debug/record/{record_id}/delete")(self.delete_debug_record)

    def get_agent_settings(self, session: SessionDep) -> AgentSettingsPublic:
        """获取所有的agent系统配置"""

        count = session.exec(select(func.count()).select_from(AgentSetting)).one()

        statement = select(AgentSetting)

        settings = session.exec(statement).all()

        pubs = [AgentSettingPublic.model_validate(setting) for setting in settings]

        return AgentSettingsPublic(data=pubs, count=count)

    def get_agent_settings_by_type(
        self, session: SessionDep, proj_type: Annotated[AgentType, Path()]
    ) -> AgentSettingsPublic:
        """获取所有的agent系统配置"""

        count = session.exec(
            select(func.count()).where(AgentSetting.agent_type == proj_type)
        ).one()

        statement = (
            select(AgentSetting)
            .where(AgentSetting.agent_type == proj_type)
            .order_by(asc(AgentSetting.section))
        )

        settings = session.exec(statement).all()

        pubs = [AgentSettingPublic.model_validate(setting) for setting in settings]

        return AgentSettingsPublic(data=pubs, count=count)

    def update_agent_setting(
        self,
        session: SessionDep,
        setting_id: Annotated[uuid.UUID, Path(description="配置id")],
        payload: Annotated[AgentSettingBase, Body(description="基本配置")],
    ) -> AgentSettingPublic:
        """更新智能体设置"""

        setting = session.get(AgentSetting, setting_id)

        if setting is None:
            raise HTTPException(404, "该配置不存在")

        setting.protocol = payload.protocol
        setting.host = payload.host
        setting.port = payload.port
        setting.app_key = payload.app_key
        setting.agent_code = payload.agent_code
        setting.agent_version = payload.agent_version
        setting.is_enable = payload.is_enable
        setting.risk_types = payload.risk_types
        setting.ref_docs = payload.ref_docs

        # 更新为新的session_id
        try:
            setting.session_id = self.update_agent_session_id(session, setting)
        except Exception as e:
            msg = f"更新会话ID时发生错误: {e}"
            logger.exception(e)
            raise HTTPException(400, msg)

        session.add(setting)
        session.commit()
        session.refresh(setting)

        return AgentSettingPublic.model_validate(setting)

    def update_agent_session_id(
        self, session: Session, agent_setting: AgentSetting
    ) -> str:
        """更新agent的回话ID"""

        # 1. 先停止旧的回话ID
        if agent_setting.session_id:
            clear_agent_session(agent_setting)  # 停止会话
            delete_agent_session(agent_setting)  # 删除会话

        # 2. 创建新的回话ID
        new_session_id = create_agent_session(agent_setting)

        return new_session_id

    def debug_agent_setting(
        self,
        session: SessionDep,
        setting_id: Annotated[uuid.UUID, Path(description="配置id")],
        payload: Annotated[AgentSettingDebug, Body(description="对话内容")],
    ) -> AgentSettingDebugRecord:
        """调试某个配置"""

        logger.info(f"{setting_id =}, 对话内容: {payload.content =}")

        setting = session.get(AgentSetting, setting_id)

        if setting is None:
            raise HTTPException(404, "该配置不存在")

        record = AgentSettingDebugRecord(
            protocol=setting.protocol,
            host=setting.host,
            port=setting.port,
            app_key=setting.app_key,
            agent_code=setting.agent_code,
            agent_version=setting.agent_version,
            agent_type=setting.agent_type,
            section=setting.section,
            req_begin_at=datetime.now(tz=pytz.timezone("Asia/Shanghai")),
        )

        try:
            url, headers, req_payload, session_id, resp = post_agent_api_core(
                setting,
                payload.content,
                attachment=payload.attchement_content or "",  # 附件内容
                timeout=payload.timeout,
            )

            record.session_id = session_id
            record.resp_done_at = datetime.now(tz=pytz.timezone("Asia/Shanghai"))
            record.req_url = url
            record.req_header = json.dumps(headers, ensure_ascii=False, indent=2)
            record.req_payload = json.dumps(req_payload, ensure_ascii=False, indent=2)

            # 记录响应
            record.resp_status = resp.status_code
            record.resp_header = json.dumps(
                dict(resp.headers), ensure_ascii=False, indent=2
            )

            # 获取耗时，以秒为单位，保留2位小数
            record.resp_spend = round(
                (record.resp_done_at - record.req_begin_at).total_seconds(), 2
            )

            try:
                record.resp_text = json.dumps(resp.json(), ensure_ascii=False, indent=2)
            except:  # noqa: E722
                record.resp_text = resp.text

            # 是否可正常解析ai接口的返回值，以指定的schema
            # 否则
            # schema可能有变，需要更新schema定义，并维护代码。

            agent_resp: AgentResponseModel | None = None

            try:
                agent_resp = parse_agent_raw_rasp(resp)
                record.resp_can_validate = True
            except:  # noqa: E722
                record.resp_can_validate = False

            # 尝试解析agent的回答
            # 1. 纯文本
            # 2. json格式的数据。
            if agent_resp is not None:
                try:
                    txt, err_msg = get_agent_resp_text(agent_resp)
                except:  # noqa: E722
                    txt, err_msg = "", "【解析agent返回值失败!】"

                record.resp_res_text = txt or err_msg

                # 尝试json加载
                if "```json" in txt:
                    try:
                        resp_text = txt.replace("```json", "").replace("```", "")
                        record.resp_res_json = json.dumps(
                            json.loads(resp_text), ensure_ascii=False, indent=2
                        )
                    except:  # noqa: E722
                        record.resp_res_json = None

        except Exception as e:
            record.error_traceback = traceback.format_exc()
            logger.error(e)

        session.add(record)
        session.commit()
        session.refresh(record)

        return record

    def get_debug_records(
        self,
        session: SessionDep,
        skip: Annotated[int, Query()] = 0,
        limit: Annotated[int, Query()] = 20,
    ) -> AgentSettingDebugRecordsPublic:
        """获取调试记录列表"""

        count = session.exec(
            select(func.count()).select_from(AgentSettingDebugRecord)
        ).one()

        statement = (
            select(AgentSettingDebugRecord)
            .order_by(desc(AgentSettingDebugRecord.create_at))
            .offset(skip)
            .limit(limit)
        )

        settings = session.exec(statement).all()

        pubs = [
            AgentSettingDebugRecordPublic.model_validate(setting)
            for setting in settings
        ]

        return AgentSettingDebugRecordsPublic(data=pubs, count=count)

    def delete_debug_record(
        self, session: SessionDep, record_id: Annotated[int, Path()]
    ) -> bool:
        """删除一条调试记录"""

        record = session.get(AgentSettingDebugRecord, record_id)

        if not record:
            return True

        session.delete(record)
        session.commit()

        return True


router = AgentSettingRoute().router
