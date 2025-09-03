import uuid
from collections import defaultdict
from datetime import datetime

from celery.result import AsyncResult
from loguru import logger
from sqlmodel import Session

from app.models.documents import (
    Document,
    DocumentContent,
    DocumentContentCreate,
    Project,
)
from app.models.enums import (
    ReviewStatus,
    SectionTitleTypeMap,
    SectionType,
)

std_section_titles = tuple(SectionTitleTypeMap.keys())


def review_err(desc: str) -> str:
    """ 错误信息用红色显示 """
    return f"<pre style='color: red;'>{desc.replace('<', '&lt;').replace('>', '&gt;')}</pre>"


def cur_time() -> str:
    """获取当前时间的字符串"""

    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def save_doc_content_to_db(
    session: Session,
    proj_name: str,
    proj_id: uuid.UUID,
    proj_version: int,
    doc_id: uuid.UUID,
    iscuser_id: str,
    docx_shtml: str,
) -> tuple[str | None, str]:
    """保存三措docx文档的内容到数据库, 并返回agent审查的celery任务ID

    效果：

    1. 将docx文档中的内容按 三措 十条 来解析
    2. 将解析到的每条的内容存储到数据库。

    Args:
        session: 数据库会话
        proj_id: 项目ID
        proj_version: 项目版本号
        doc_id: 数据库中存储的文档ID
        iscuser_id: isc用户ID
        docx_shtml: 三措文档解析后的simple html内容

    Returns:
        保存的DocumentContent实例。
    """
    process_msgs: list[str] = []

    txt_lines = docx_shtml.split("\n")

    # 当前section
    curren_section: SectionType = SectionType.head

    section_contents: list[str] = []

    document_contents: list[DocumentContent] = []

    # 保存所有文档所有txt内容
    logger.info(f"{type(docx_shtml) = }")

    msg = f"项目:【{proj_name}】【第{proj_version}次提交】开始处理docx文件..."
    process_msgs.append(f"{cur_time()} - {msg}")
    logger.info(msg)

    doc_all_content = save_document_content(
        session, proj_id, proj_version, doc_id, iscuser_id, SectionType.all, docx_shtml
    )
    document_contents.append(doc_all_content)

    # 文档的节名称和节内容ID的映射，要发送给异步审核函数。
    agent_params: dict[str, str] = {SectionType.all.value: doc_all_content.id.hex}

    # 缓存已解析到的section内容
    section_content_cache: dict[SectionType, list[str]] = defaultdict(list)

    # 保存文档各section内容
    for line in txt_lines:
        unwrap_line = line.strip()

        # 使用 any() 和 in 操作符
        section_title = find_section_title(unwrap_line)

        if section_title:
            # 保存section内容
            content = "\n".join(section_contents)
            section_content_cache[curren_section].append(content)
            section_contents.clear()  # 保存之后要清空

            msg = f"项目:【{proj_name}】【第{proj_version}次提交】找到节: {review_err(section_title)}"
            process_msgs.append(f"{cur_time()} - {msg}")
            logger.info(msg)

            # 将下一个的section标题添加进去
            section_contents.append(line)

            # 赋予新的section
            curren_section = SectionTitleTypeMap[section_title]
        else:
            section_contents.append(line)

    # 扫尾，保存最后一个块
    content = "\n".join(section_contents)

    section_content_cache[curren_section].append(content)

    # 保存每个section中对应的最多的内容的content
    logger.info(f"{section_content_cache = }")
    for section, contents in section_content_cache.items():
        # 最长的内容
        content = max(contents, key=len)

        dc = save_document_content(
            session, proj_id, proj_version, doc_id, iscuser_id, section, content
        )
        document_contents.append(dc)
        agent_params[section.value] = dc.id.hex

    project = session.get(Project, proj_id)

    assert project is not None, "项目不存在"

    # 更新项目状态和进度
    project.review_begin_at = datetime.now()
    project.review_status = ReviewStatus.UNREVIEWED
    project.review_percent = 20

    session.add(project)
    session.commit()

    msg = f"项目:【{proj_name}】【第{proj_version}次提交】更新项目状态和进度为: 【{review_err(ReviewStatus.UNREVIEWED.value)}】"
    process_msgs.append(f"{cur_time()} - {msg}")
    logger.info(msg)

    # 构建异步审核函数的参数
    kwargs = {
        "proj_name": project.name,
        "proj_version": project.version,
        "proj_type": project.type.value,
        "proj_id": project.id.hex,
    }

    # todo: 调用智能体接口，审核各部分内容并生成建议。
    # 发送celery任务，调用agent对文档内容进行审查

    # celery 任务
    from app.tasks.reviews import review_by_agent

    ares: AsyncResult = review_by_agent.delay(agent_params, **kwargs)  # type: ignore

    taskid: str | None = ares.id

    msg = f"项目:【{proj_name}】【第{proj_version}次提交】提交agent审核任务, id: {review_err(taskid or '')}"
    process_msgs.append(f"{cur_time()} - {msg}")
    logger.info(msg)

    document = session.get(Document, doc_id)

    if document is not None:
        document.task_id = uuid.UUID(taskid) if taskid else None
        session.add(document)
        session.commit()

    return taskid, '\n'.join(process_msgs)


def save_document_content(
    session: Session,
    proj_id: uuid.UUID,
    proj_version: int,
    doc_id: uuid.UUID,
    iscuser_id: str,
    section: SectionType,
    content: str,
) -> DocumentContent:
    """保存文档内容"""

    dc_create = DocumentContentCreate(
        section=section,
        content=content,
        suggestion="",
    )

    update = {
        "proj_id": proj_id,
        "proj_version": proj_version,
        "doc_id": doc_id,
        "iscuser_id": iscuser_id,
    }
    dc = DocumentContent.model_validate(dc_create, update=update)

    try:
        session.add(dc)
        session.commit()
        session.refresh(dc)
    except Exception as e:
        logger.exception(f"保存文档内容失败! {e}")
        session.rollback()

    return dc


def find_section_title(line: str) -> str | None:
    """找到三措十条中对应的某一条

    如:

        十、现场作业示意图（附图）

    对应:

        十、现场作业示意图
    """
    for keyword in std_section_titles:
        # 1. 将空格去掉、括号替换为英文的括号。
        _line = line.replace(" ", "").replace('）',')').replace('（', '(').replace('竣', '峻')
        # 2. 不要 '一、', '二、', '三、', '1、', '2、', '3、' 等前缀
        # 3. 确保是【节内容标题】单独占一行。
        if keyword[2:] in _line and len(_line) == len(keyword):
            logger.info(f"{keyword} => 匹配到的行: {_line}")
            return keyword

    return None
