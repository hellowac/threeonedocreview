import html
import json
import uuid
from datetime import datetime

import requests  # type: ignore
from celery import Task  # type: ignore
from loguru import logger
from requests.models import Response as RequestsResponse
from sqlmodel import Session, or_, select

from app.api.schems import AgentResponseModel, RunAgentMessagePayload, RunAgentPayload
from app.api.utils import (
    clear_agent_session,
    create_agent_session,
    delete_agent_session,
)
from app.core import celery_app
from app.core.config import settings
from app.core.db import engine
from app.models.agentsetting import AgentSetting
from app.models.documents import (
    Document,
    DocumentContent,
    DocumentContentReview,
    Project,
)
from app.models.enums import (
    AgentType,
    FileCategory,
    ForSection,
    ForSectionTitleMap,
    ProjectTypeEnum,
    ReviewStatus,
    SectionContextRelated,
    SectionPriorityMap,
    SectionTitleTypeMap,
    SectionType,
)
from app.tasks.common import cur_time, review_err

# 模拟数据

std_all_sections = set(SectionTitleTypeMap.values())


@celery_app.task(bind=True)
def review_by_agent(
    self: Task,  # noqa: ARG001
    agent_params: dict[str, str],
    *,
    proj_name: str,  # noqa: ARG001
    proj_version: int,  # noqa: ARG001
    proj_type: str,  # noqa: ARG001
    proj_id: str,  # noqa: ARG001
) -> str:
    """调用远程AI的智能体接口

    # todo: ai建议完，则要判断所有section中的内容是否都建议完，建议完则要更新项目/工程的审批状态。

    Args:
        self: CeleryTask实例
        agent_params: 文档所属节: 文档节内容ID 的字典。 (str -> uuid_str),
        proj_name: 项目名称
        proj_version: 第几次提交
        proj_type: 项目类型
        proj_id: 项目ID, uuid_str
    """

    found_sections = {SectionType(value) for value in agent_params.keys()}

    process_msgs = []

    with Session(engine) as session:
        # 少解析到的section
        miss_sections = std_all_sections - found_sections

        all_doc_content_id = uuid.UUID(agent_params[SectionType.all.value])
        doc_all_content = session.get(DocumentContent, all_doc_content_id)

        assert doc_all_content is not None, "获取文档内容失败"

        project = session.get(Project, doc_all_content.proj_id)
        if not project:
            msg = f"项目:【{doc_all_content.proj_id}】 不存在，无法审查."
            raise ValueError(msg)
        else:
            # 记录一下
            msg = f"项目:【{project.name}】【第{project.version}次提交】开始审查..."
            process_msgs.append(f"{cur_time()} - {msg}")
            logger.info(msg)

        # 是否发生过的异常 或 提取章节失败
        raised_error_or_miss_section: bool = False
        miss_section_suggestion = ""

        # 缺少相关的节，直接返回
        if miss_sections:
            # 这里会更新project 的 suggestion
            miss_section_suggestion = suggestion_by_miss_section(
                session, doc_all_content, miss_sections
            )

            # 记录一下
            msg = f"项目:【{project.name}】【第{project.version}次提交】的 {review_err('标题不规范，部分内容提取失败')}，将进行有限审查..."
            process_msgs.append(f"{cur_time()} - {msg}")
            logger.info(msg)

        # 构建节和内容的映射
        dcontent_map: dict[SectionType, DocumentContent] = {}
        for title, doc_id in agent_params.items():
            _dcontent = session.get(DocumentContent, uuid.UUID(doc_id))
            assert _dcontent is not None
            dcontent_map[SectionType(title)] = _dcontent

        completed_doc_contents: list[DocumentContent] = []

        for title, stype in SectionTitleTypeMap.items():
            logger.info(f"审查 【{title}】部分的内容....")
            doc_content_id_str = agent_params.get(stype.value)

            if not doc_content_id_str:
                msg = f"项目:【{project.name}】【第{project.version}次提交】中【{title}】的{review_err('内容提取失败')}，无法审查."
                process_msgs.append(f"{cur_time()} - {msg}")
                logger.warning(msg)
                continue

            doc_content = dcontent_map[stype]

            if not doc_content:
                msg = f"项目:【{project.name}】【第{project.version}次提交】中【{title}：{doc_content.id}】的{review_err('内容提取失败')}，无法审查."
                process_msgs.append(f"{cur_time()} - {msg}")
                logger.warning(msg)
                continue

            # 记录一下，将来在页面中好搜索
            msg = f"项目:【{project.name}】【第{project.version}次提交】的【{doc_content.section.value}】开始审查."
            process_msgs.append(f"{cur_time()} - {msg}")
            logger.info(msg)

            review_proj_type = {
                ProjectTypeEnum.TRNAS: AgentType.transmission,
                ProjectTypeEnum.DISTRIBUTION: AgentType.distribute,
                ProjectTypeEnum.SUBSTATION: AgentType.substation,
            }[doc_content.project.type]

            review_section = {
                SectionType.one: ForSection.one,
                SectionType.two: ForSection.two,
                SectionType.three: ForSection.three,
                SectionType.four: ForSection.four,
                SectionType.five: ForSection.five,
                SectionType.six: ForSection.six,
                # 第七节单独审核4次
                SectionType.seven: (
                    ForSection.sevenone,
                    ForSection.seventwo,
                    ForSection.seventhree,
                    ForSection.sevenfour,
                ),
                SectionType.eight: ForSection.eight,
                SectionType.nine: ForSection.nine,
                SectionType.ten: ForSection.ten,
            }[doc_content.section]

            try:
                if isinstance(review_section, tuple):
                    err_msg = ""
                    for _review_section in review_section:
                        _, _err_msg = request_remote_agent(
                            session,
                            project,
                            doc_content,
                            dcontent_map,
                            review_proj_type,
                            _review_section,
                        )

                        err_msg += _err_msg
                else:
                    _, err_msg = request_remote_agent(
                        session,
                        project,
                        doc_content,
                        dcontent_map,
                        review_proj_type,
                        review_section,  # type: ignore
                    )

                if err_msg:
                    raised_error_or_miss_section = True
                    msg = f"项目:【{project.name}】【第{project.version}次提交】的【{doc_content.section.value}】agent 审查异常, 错误: {review_err(html.escape(err_msg))}"
                    process_msgs.append(f"{cur_time()} - {msg}")
                    logger.info(msg)
            except Exception as e:
                msg = f"项目:【{project.name}】【第{project.version}次提交】的【{doc_content.section.value}】审查异常, 错误: {review_err(html.escape(str(e)))}"
                process_msgs.append(f"{cur_time()} - {msg}")
                logger.exception(msg)

                doc_content.suggestion = f"审查异常: {review_err(html.escape(str(e)))}"
                session.add(doc_content)
                session.commit()
                session.refresh(doc_content)

                # 继续审查， 不过要标识发生过错误，表示【算法审查失败】！
                raised_error_or_miss_section = True

            # 记录一下，将来在页面中好搜索
            msg = f"项目:【{project.name}】【第{project.version}次提交】的【{doc_content.section.value}】审查完成."
            process_msgs.append(f"{cur_time()} - {msg}")
            logger.info(msg)

            completed_doc_contents.append(doc_content)

        # 根据完成的内容审查，生成一个针对该文档的概述。同时同步到项目的审查结果（建议）。
        content_suggestions: list[str] = []
        for content in completed_doc_contents:
            content_suggestions.append(
                f"# {content.section}"
            )  # 添加节标题，markdown格式
            content_suggestions.append(content.suggestion)

        combined_suggestion = combine_ai_suggestion(session, content_suggestions)

        # 同步文档整体内容的建议
        # 合并缺失节的建议
        review_suggestion = combined_suggestion
        if miss_section_suggestion:
            review_suggestion = f"{miss_section_suggestion}\n{combined_suggestion}"

        doc_all_content.suggestion = review_suggestion
        session.add(doc_all_content)
        session.commit()
        session.refresh(doc_all_content)

        # 同步项目的该版本的文档的建议
        review_status = ReviewStatus.AI_REVIEW_PASSED
        review_percent = 80
        if raised_error_or_miss_section:
            review_percent = 60
            review_status = ReviewStatus.AI_REVIEW_NOTPASS

        document = doc_all_content.document
        document.review_suggestion = review_suggestion
        document.review_done_at = datetime.now()
        document.review_percent = review_percent
        document.review_status = review_status

        session.add(document)
        session.commit()
        session.refresh(document)

        # 同步项目的整体建议
        project.review_suggestion = review_suggestion
        project.review_done_at = datetime.now()
        project.review_percent = review_percent
        project.review_status = review_status

        session.add(project)
        session.commit()
        session.refresh(project)

    # 记录一下，将来在页面中好搜索
    msg = f"项目:【{project.name}】【第{project.version}次提交】审查完成."
    process_msgs.append(f"{cur_time()} - {msg}")
    logger.info(msg)

    return "\n".join(process_msgs)


def suggestion_by_miss_section(
    session: Session, dcontent: DocumentContent, miss_sections: set[SectionType]
) -> str:
    """根据缺少的section生成md格式的建议，建议到content中"""

    # 缺失的标题
    sorted_miss_sections = sorted(miss_sections, key=lambda x: SectionPriorityMap[x])
    miss_sections_str = "\n".join(
        [f"* {section.value}" for section in sorted_miss_sections]
    )

    # 所有应该有的标题
    sorted_std_sections = sorted(std_all_sections, key=lambda x: SectionPriorityMap[x])
    std_sections_str = "\n".join(
        [f"* {section.value}" for section in sorted_std_sections]
    )

    suggestion = "\n".join(
        [
            "# 提取相关节标题失败",
            "",
            miss_sections_str,
            "",
            "请按照《国网海西供电公司施工“三措”计划管理实施细则（试行）.pdf》文件中第十四条大纲内容编写文档。",
            "",
            "标题大纲应遵循:",
            "",
            std_sections_str,
            "",
        ]
    )

    dcontent.suggestion = suggestion
    session.add(dcontent)

    # 将相关文档的审核状态更新为审核不通过
    doc = session.get(Document, dcontent.doc_id)

    if doc is not None:
        doc.review_status = ReviewStatus.AI_REVIEW_NOTPASS
        doc.review_suggestion = suggestion
        doc.review_done_at = datetime.now()
        doc.review_percent = 100
        session.add(doc)

        # 增加建议详细
        review = DocumentContentReview(
            iscuser_id=doc.iscuser_id,
            proj_id=doc.proj_id,
            proj_version=doc.proj_version,
            doc_id=doc.id,
            content_id=dcontent.id,
            section=dcontent.section,
            question="未按《国网海西供电公司施工“三措”计划管理实施细则（试行）.pdf》编写三措文档标题。",
            question_tag="文档标题错误",
            feedback="请按照相关标准，编写文档标题。",
            feedback_tag="完善文档标题",
            ai_error="",
        )
        session.add(review)

    session.commit()

    return suggestion


def request_remote_agent(
    session: Session,
    proj: Project,
    dcontent: DocumentContent,
    dcontent_map: dict[SectionType, DocumentContent],
    review_proj_type: AgentType,
    review_section: ForSection,
) -> tuple[DocumentContent, str]:
    """请求远程的智能体进行审查

    1. 获取agent的配置
    2. 构造agent需要的参数
    3. 解析agent的返回结果

    Args:
        dcontent: 文档内容对象。
    """
    logger.info(
        f"审查【{proj.name}({proj.version})】的【{dcontent.section.value}】 部分中..."
    )

    # 模拟ai审查需要的时间
    # seconds = random.randint(0, 7)
    # time.sleep(seconds)
    # logger.info(f"随机sleep {seconds} 秒")

    # -------- 该节的概述 -------------
    # setion的概述: 调用ai的section审核概述。
    # dcontent.suggestion = mock_content_feedbacks[dcontent.section][random.randint(0, 9)]

    # 审查该节过程中产生的错误:
    err_msgs: list[str] = []

    # 对于不支审查的节，生成概览提示
    if dcontent.section not in SectionContextRelated:
        logger.info(f"该节暂不支持审查: {dcontent.section}")

        dcontent.suggestion = "该节暂不支持审查！"
        session.add(dcontent)
        session.commit()
        session.refresh(dcontent)

        return dcontent, ""

    # 构造有上下文的请求消息
    related_sections = SectionContextRelated[dcontent.section]
    context_messages: list[str] = []

    for r_section in related_sections:
        if r_section not in dcontent_map:
            raise Exception(
                f"【{dcontent.section.value}】节审查，依赖的相关节 【{r_section.value}】获取失败, 无法审查！！"
            )
        context_messages.append(dcontent_map[r_section].content)

    # 直接审查获取结果，调用审核各个节的智能体，不需要封装成json了。 2025-08-12 19:06:53
    # contexted_message = {
    #     "section": review_section,
    #     "content": "\n".join(context_messages),
    # }
    # contexted_message_json_str = json.dumps(contexted_message, ensure_ascii=False)

    contexted_message_json_str = "\n".join(context_messages)
    logger.info(f"审查内容: {contexted_message_json_str}")

    # 获取附件内容。
    attachment = get_attachment_from_db(session, proj)

    # -------- 该节的概述， 不需要了 ----------

    # 根据智能体设置请求审查相关section
    # agent_setting = get_agent_setting(session, dcontent.project.type, dcontent.section)
    # agent_resp = post_agent_api(agent_setting, contexted_message_json_str)

    # suggestion, err_msg = get_agent_resp_text(agent_resp)

    # # 第七节分了4次审，所以要累加
    # if dcontent.section == SectionType.seven:
    #     dcontent.suggestion = f"{dcontent.suggestion}\n{suggestion}"
    # else:
    #     dcontent.suggestion = suggestion

    # if err_msg:
    #     err_msgs.append(err_msg)

    # session.add(dcontent)
    # session.commit()
    # session.refresh(dcontent)

    # --------- 该节的详细 --------------
    agent_setting = get_agent_setting(session, review_proj_type, review_section)

    # 该智能体未启用时，直接退出
    if not agent_setting.is_enable:
        err_msgs.append(
            f"【{dcontent.project.type.name}】-【{dcontent.section.name}】的智能体尚未支持审查或未启用！"
        )

        return dcontent, ";".join(err_msgs)

    # 该message应为agent返回的文本, 从该文本中extract 问题/建议详细
    # agent_resp = post_agent_api(agent_setting, dcontent.suggestion)
    agent_resp = post_agent_api(
        agent_setting, contexted_message_json_str, attachment=attachment
    )

    # 预期为json格式的数据: [{question: xxx, question_tag: xxx, ...}, ...]
    # {
    #     "question": "未明确紧急情况下的撤离路线和集合点。",
    #     "question_tag": "撤离路线不明",
    #     "feedback": "请详细说明紧急情况下人员应遵循的撤离路线及安全集合点位置。",
    #     "feedback_tag": "补充撤离路线信息",
    #     "ai_error": "",
    # }

    # 实际返回的json字符串总会包含在 ```json xxx ``` 块中，所以需要替换，然后json.loads
    resp_text, err_msg = get_agent_resp_text(agent_resp)
    if err_msg:
        err_msgs.append(err_msg)

    resp_text = resp_text.replace("```json", "").replace("```", "")
    logger.info(f"节详细内容，处理后: {resp_text}")

    # 实际格式如:
    # [
    #     {
    #         "risk_type": "有错别字",  # 问题类型，简述
    #         "project_status": "所有安全工器具的编号字段为空",# 方案现状（原文，省略的），简述
    #         "project_source_location": "施工安全保证措施-(一)-安全工器具配置",# 原文出处（末级标题，不要原文）
    #         "evidence_quote": "安全工器具应进行编号管理，确保每件工器具的唯一性。",  # 标准要求，引用文件内容，（省略的）
    #         "source_document_name": "《国家电网公司电力安全工器具管理规定》", # 出处文件，文件名字
    #         "source_section_number": "第四章 日常管理",     # 来源标题
    #         "modification_suggestion": "为所有安全工器具补充唯一编号，并记录在清单中。",  # 修改意见
    #         "risk_type_class": "技术参数缺失",  # 问题标签，对risk_type进行抽象提取总结，可视化用，用来展示三措编制人员存在哪些问题
    #         "evidence_quote_class": "安全管理制度"  # 引用标准标签，对evidence_quote进行抽象提取总结，可视化用，用来展示三措哪些规章制度编写人员不熟悉
    #     },
    #     {
    #         "risk_type": "审查内容中存在错别字",
    #         "project_status": "项木安全员：裴有梁 13897064503",
    #         "project_source_location": "末级标题",
    #         "evidence_quote": "None",
    #         "source_document_name": "None",
    #         "source_section_number": "None",
    #         "modification_suggestion": "应将 \"项木安全员\" 修改为 \"项目安全员\"，确保职责名称书写正确",
    #         "risk_type_class": "内容包含错别字",
    #         "evidence_quote_class": "None"
    #     },
    #     ....
    # ]
    try:
        feedbacks: list[dict] = json.loads(resp_text)
    except Exception as e:
        logger.exception(f"反序列化节详细内容(list[dict])失败: {e}")
        feedbacks = []

    # 先根据模拟数据来, 再针对该概述，生成具体问题/反馈条目。
    # 调用ai审核的结构化结果描述。
    # feedbacks = random.choices(
    #     mock_section_feedbacks[dcontent.section], k=random.randint(1, 10)
    # )
    for feedback in feedbacks:
        review = DocumentContentReview(
            iscuser_id=dcontent.iscuser_id,
            proj_id=dcontent.proj_id,
            proj_version=dcontent.proj_version,
            doc_id=dcontent.doc_id,
            content_id=dcontent.id,
            section=dcontent.section,
            question=feedback.get("risk_type"),  # 问题详细
            question_tag=feedback.get("risk_type_class"),  # 问题标签
            feedback=feedback.get("modification_suggestion"), # 建议反馈详细内容
            feedback_tag=feedback.get("evidence_quote_class"), # 建议反馈标签
            reference_filename=feedback.get("source_document_name"),  # 引用文件名
            reference_content=feedback.get("evidence_quote"), # 引用文件内容
            reference_location=feedback.get("source_section_number"),  # 引用文件中内容的位置
            source_text=feedback.get('project_status'), # 原文内容，简述
            source_location=feedback.get('project_source_location'),  # 原文内容位置
            ai_error=feedback.get("ai_error"),
        )

        session.add(review)
        session.commit()

    return dcontent, ";".join(err_msgs)


def get_attachment_from_db(session: Session, proj: Project) -> str:
    """获取指定项目的附件的内容。"""

    statement = select(Document.id).where(
        Document.proj_id == proj.id,
        Document.proj_version == proj.version,
        # or_(
        #     Document.file_category == FileCategory.FEASIBIBITY,
        #     Document.file_category == FileCategory.SURVEY,
        #     Document.file_category == FileCategory.OTHER,
        # ),
        Document.file_category.in_(  # type: ignore
            (FileCategory.FEASIBIBITY, FileCategory.SURVEY, FileCategory.OTHER)
        ),
    )
    attchement_docs_id = list(session.exec(statement).all())

    if not attchement_docs_id:
        return ""

    statement1 = select(DocumentContent.content).where(
        DocumentContent.id.in_(attchement_docs_id)  # type: ignore
    )
    dcs = list(session.exec(statement1).all())

    return "\n".join(dcs)


# 文档/项目的概述：调用AI将多个suggestion提炼成1个suggestion
def combine_ai_suggestion(session: Session, suggestions: list[str]) -> str:
    """将某个文档各个节的ai建议，合并，并提炼成一句话。"""

    long_suggestion = "\n".join(suggestions)  # noqa: F841

    # 直接返回拼接的各个节的概述，agent目前不好对各个节的概述内容在做提炼，容易出现幻觉。
    return long_suggestion

    # agent_setting = get_agent_setting(session, ForSection.document_overview)
    # agent_resp = post_agent_api(agent_setting, long_suggestion)

    # agent_resp_text, err_msg = get_agent_resp_text(agent_resp)

    # # 先返回模拟数据
    # # return mock_document_feedbacks[random.randint(0, 9)]
    # return agent_resp_text


def get_agent_setting(
    session: Session, proj_type: AgentType, docsection: ForSection
) -> AgentSetting:
    """获取agent的配置"""

    statement = select(AgentSetting).where(
        AgentSetting.agent_type == proj_type, AgentSetting.section == docsection
    )
    agent_setting = session.exec(statement).first()

    if agent_setting is None:
        raise ValueError(f"获取Agent配置失败, {proj_type.value} - {docsection.value}")

    return agent_setting


def post_agent_api(
    agent_setting: AgentSetting,
    _message: str,
    attachment: str = "",
    is_chat: bool = False,
) -> AgentResponseModel:
    """请求智能体接口并返回结果"""

    url, headers, payload, session_id, resp = post_agent_api_core(
        agent_setting, _message, attachment=attachment, is_chat=is_chat
    )

    logger.info(f"调用agent 返回: {resp.text = }")

    if resp.status_code != 200:
        raise Exception(f"请求agent接口失败: {resp.text}")

    return parse_agent_raw_rasp(resp)


def parse_agent_raw_rasp(resp: RequestsResponse) -> AgentResponseModel:
    agent_resp = AgentResponseModel.model_validate(resp.json())

    if not agent_resp.success:
        raise Exception(
            f"agent执行失败, 返回数据:【{review_err(html.escape(resp.text))}】"
        )

    if (
        agent_resp.data
        and agent_resp.data.error
        and agent_resp.data.error.content
        and not agent_resp.data.message
    ):
        raise Exception(
            f"agent执行错误, {agent_resp.data.error.content.errorName}({agent_resp.data.error.content.errorCode}): {agent_resp.data.error.content.errorMsg}"
        )

    return agent_resp


def post_agent_api_core(
    agent_setting: AgentSetting,
    _message: str,
    attachment: str = "",
    is_chat: bool = False,
    timeout: float | None = None,
) -> tuple[str, dict, dict, str, RequestsResponse]:
    """请求智能体接口并返回结果

    Args:
        agent_setting (AgentSetting): 智能体设置实例。
        _message (str): 对话的内容。
        attachment (str): 附件内容。
        timout (float): 超时时间， 单位为秒(S), 默认为None, 无超时限制。

    Returns:
        5个值的元祖，分别代表:

        - 请求的url,
        - 请求的headers,
        - 请求的payload,
        - 使用的session_id,
        - 请求的响应，resp
    """

    url = settings.build_agent_api(
        agent_setting.protocol, agent_setting.host, agent_setting.port
    )

    headers = {
        "Authorization": f"Bearer {agent_setting.app_key}",
        "Content-Type": "application/json",
    }

    # 创建1个新的session, 用于当前请求，防止上一个session_id执行超时后，影响后面的请求。
    new_session_id = create_agent_session(agent_setting)

    # 封装agent需要的结构, 如果是智能体助手，则不需要。
    if is_chat:
        message = RunAgentMessagePayload(text=_message)

    # agent 会用json.loads 来加载数据。
    else:
        message = RunAgentMessagePayload(
            text=json.dumps(
                {
                    "section": ForSectionTitleMap[agent_setting.section],   # 对应的节
                    "examine_content": _message,                    # 审核的内容
                    "attachment": attachment,                       # 附件信息
                    "risk_type_class": agent_setting.risk_types or "",  # 设置的风险类型
                    "evidence_quote_class": agent_setting.ref_docs or "",  # 设置的引用文件
                },
                ensure_ascii=False,
            )
        )

    payload = RunAgentPayload(
        sessionId=new_session_id, stream=False, message=message
    ).model_dump(mode="json")

    try:
        resp = requests.post(url, json=payload, headers=headers, timeout=timeout)

        return url, headers, payload, new_session_id, resp

    finally:
        clear_agent_session(agent_setting, new_session_id)
        logger.info(f"清理新创建的agent session_id: {new_session_id} 成功!")
        delete_agent_session(agent_setting, new_session_id)
        logger.info(f"删除新创建的agent session_id: {new_session_id} 成功!")


def get_agent_resp_text(agent_resp: AgentResponseModel) -> tuple[str, str]:
    """获取agent返回的第一个message中的文本"""

    assert agent_resp.data is not None, "agent 返回的数据(data)为空"

    assert agent_resp.data.message is not None, "agent 返回的消息为空"

    agent_resp_content = agent_resp.data.message.content[0]

    if agent_resp_content.type != "text":
        raise Exception("获取agent返回失败, 内容不是text")

    if agent_resp_content.text is None or not agent_resp_content.text.value:
        raise Exception("获取agent返回失败, 内容为空")

    txt = agent_resp_content.text.value
    err_msg = ""
    try:
        # 这里的value值总是格式如 '[xxx]' 的值，所以这里要json.loads 然后取索引为 0 的文本.
        txt = json.loads(txt)[0]
    except Exception as e:
        err_msg = f"反序列化agent返回(list[str])失败: {e}"
        logger.exception(err_msg)

        err_msg += f"\n返回的txt值为:{txt}"

    return txt, err_msg
