import json
import random
import uuid
from typing import Annotated

from fastapi import APIRouter, Body, Depends, FastAPI, Header, HTTPException
from loguru import logger

from app.api.schems import (
    AgentResponseDataErrorContentModel,
    AgentResponseDataErrorModel,
    AgentResponseDataMessageContentImageModel,
    AgentResponseDataMessageContentModel,
    AgentResponseDataMessageContentTextModel,
    AgentResponseDataMessageModel,
    AgentResponseDataModel,
    AgentResponseDataThoughtsContentModel,
    AgentResponseDataThoughtsModel,
    AgentResponseModel,
    ClearSessionPayload,
    ClearSessionResponseModel,
    CreateSessionPayload,
    CreateSessionResponseDataModel,
    CreateSessionResponseModel,
    RunAgentPayload,
)
from app.models.enums import SectionTitleTypeMap
from mock_agent_data import (
    mock_content_feedbacks,
    mock_document_feedbacks,
    mock_feedbacks,
)

app = FastAPI()

# -------------- 注入依赖 --------------


def get_appkey_dep(
    Authorization: Annotated[str, Header()], Content_Type: Annotated[str, Header()]
) -> str:
    """获取header头中的app_key"""

    if Content_Type != "application/json":
        raise HTTPException(400, "content-type 应该为 application/json")

    app_key = Authorization.replace("Bearer ", "")

    return app_key


AppKeyDep = Annotated[str, Depends(get_appkey_dep)]


# ---------------------路由函数定义----------------------------

router = APIRouter(prefix="/xlm-gateway-bo-ihi/sfm-api-gateway/gateway/agent/api")

app_key_section_detail = "jm77cyhyp4isp095skx85q1mcjs0rsf6"
app_key_section_overview = "q05oo8cko230bm5mrr20bpokbwfty1ph"
app_key_document_overview = "l6i7ids5p9pwygs7rcvr00aovohctbc3"
app_key_qa = "l6i7iss5p9pwugs7rcvr70aovhhctbc3"

registed_app_keys: set[str] = {
    app_key_section_detail,
    app_key_section_overview,
    app_key_document_overview,
    app_key_qa,
}
registed_uuid: set[str] = set()


@router.post("/createSession")
def createSession(
    auth: AppKeyDep, payload: Annotated[CreateSessionPayload, Body()]
) -> CreateSessionResponseModel:
    if auth not in registed_app_keys:
        raise HTTPException(400, "该app key 不存在")

    session_id = str(uuid.uuid4())

    logger.info(
        f"Auth: {auth = }, {payload.agentCode = }, {payload.agentVersion =} => {session_id = }"
    )

    registed_uuid.add(session_id)

    data = CreateSessionResponseDataModel(uniqueCode=session_id)
    resp = CreateSessionResponseModel(success=True, data=data)

    return resp


@router.post("/run")
def agent_run(
    appkey: AppKeyDep, payload: Annotated[RunAgentPayload, Body()]
) -> AgentResponseModel:
    if appkey not in registed_app_keys:
        raise HTTPException(400, "该app key 不存在")

    # if payload.sessionId not in registed_uuid:
    #     raise HTTPException(400, "该session ID 不存在")

    if appkey == app_key_section_detail:
        items = random.choices(mock_feedbacks, k=random.randint(1, 10))

        # resp_text = json.dumps(items)

        str1 = '{"errorMessages":[],"success":true,"data":{"message":{"id":"eed487d0-0900-4d75-bbab-ffe7c1bf2fde","gmtCreate":"2025-07-14T08:39:32.329+00:00","sessionId":"f9b2208f-846b-43a4-a428-4bb3673d2152","requestId":"5259d34f-6049-4399-bfbf-40c060626659","role":"assistant","content":[{"index":null,"type":"text","text":{"value":"[\\"\\\\n\\\\n```json\\\\n[\\\\n  {\\\\n    \\\\\\"catalog_name\\\\\\": \\\\\\"工程概况\\\\\\",\\\\n    \\\\\\"question\\\\\\": \\\\\\"缺失地理位置信息：内容未明确工程所在的地市/区、县、乡镇/街道及周边重点参照物（如道路、建筑等）。\\\\\\",\\\\n    \\\\\\"question_tag\\\\\\": \\\\\\"内容缺失\\\\\\",\\\\n    \\\\\\"question_exist\\\\\\": \\\\\\"true\\\\\\",\\\\n    \\\\\\"feedback\\\\\\": \\\\\\"补充工程地理位置，例如“本工程位于XX市XX区XX街道，邻近XX变电站/XX道路，涉及拆除同塔双回线路导、地线共XX公里”。\\\\\\",\\\\n    \\\\\\"feedback_exist\\\\\\": \\\\\\"true\\\\\\",\\\\n    \\\\\\"feedback_tag\\\\\\": \\\\\\"补充内容\\\\\\",\\\\n    \\\\\\"filename\\\\\\": \\\\\\"无支撑材料。\\\\\\",\\\\n    \\\\\\"content\\\\\\": \\\\\\"无支撑材料。\\\\\\",\\\\n    \\\\\\"ai_error\\\\\\": \\\\\\"\\\\\\"\\\\n  },\\\\n  {\\\\n    \\\\\\"catalog_name\\\\\\": \\\\\\"工程概况\\\\\\",\\\\n    \\\\\\"question\\\\\\": \\\\\\"工程规模描述不完整：仅提及拆除线路段，未说明具体规模（如线路长度、杆塔数量等）。\\\\\\",\\\\n    \\\\\\"question_tag\\\\\\": \\\\\\"内容不完整\\\\\\",\\\\n    \\\\\\"question_exist\\\\\\": \\\\\\"true\\\\\\",\\\\n    \\\\\\"feedback\\\\\\": \\\\\\"补充工程规模，例如“拆除线路总长XX米，涉及杆塔XX基”。\\\\\\",\\\\n    \\\\\\"feedback_exist\\\\\\": \\\\\\"true\\\\\\",\\\\n    \\\\\\"feedback_tag\\\\\\": \\\\\\"补充内容\\\\\\",\\\\n    \\\\\\"filename\\\\\\": \\\\\\"无支撑材料。\\\\\\",\\\\n    \\\\\\"content\\\\\\": \\\\\\"无支撑材料。\\\\\\",\\\\n    \\\\\\"ai_error\\\\\\": \\\\\\"\\\\\\"\\\\n  },\\\\n  {\\\\n    \\\\\\"catalog_name\\\\\\": \\\\\\"施工作业特点\\\\\\",\\\\n    \\\\\\"question\\\\\\": \\\\\\"周围环境描述缺失：未提及工程周边环境（如邻近居民区、交通要道、地形条件等）。\\\\\\",\\\\n    \\\\\\"question_tag\\\\\\": \\\\\\"内容缺失\\\\\\",\\\\n    \\\\\\"question_exist\\\\\\": \\\\\\"true\\\\\\",\\\\n    \\\\\\"feedback\\\\\\": \\\\\\"补充环境信息，例如“作业区域临近农田/居民区，需注意机械操作对周边的影响”或“现场地形为丘陵，需加强设备固定措施”。\\\\\\",\\\\n    \\\\\\"feedback_exist\\\\\\": \\\\\\"true\\\\\\",\\\\n    \\\\\\"feedback_tag\\\\\\": \\\\\\"补充内容\\\\\\",\\\\n    \\\\\\"filename\\\\\\": \\\\\\"无支撑材料。\\\\\\",\\\\n    \\\\\\"content\\\\\\": \\\\\\"无支撑材料。\\\\\\",\\\\n    \\\\\\"ai_error\\\\\\": \\\\\\"\\\\\\"\\\\n  },\\\\n  {\\\\n    \\\\\\"catalog_name\\\\\\": \\\\\\"施工作业特点\\\\\\",\\\\n    \\\\\\"question\\\\\\": \\\\\\"作业特点未突出特殊性：现有内容为通用性描述，未结合本工程具体特点（如双回线路同步拆除风险）。\\\\\\",\\\\n    \\\\\\"question_tag\\\\\\": \\\\\\"描述不具体\\\\\\",\\\\n    \\\\\\"question_exist\\\\\\": \\\\\\"true\\\\\\",\\\\n    \\\\\\"feedback\\\\\\": \\\\\\"增加针对性说明，例如“同塔双回线路拆除需同步协调停电，避免误碰带电线路”或“需采用分段牵引法防止导线坠落”。\\\\\\",\\\\n    \\\\\\"feedback_exist\\\\\\": \\\\\\"true\\\\\\",\\\\n    \\\\\\"feedback_tag\\\\\\": \\\\\\"增加说明\\\\\\",\\\\n    \\\\\\"filename\\\\\\": \\\\\\"无支撑材料。\\\\\\",\\\\n    \\\\\\"content\\\\\\": \\\\\\"无支撑材料。\\\\\\",\\\\n    \\\\\\"ai_error\\\\\\": \\\\\\"\\\\\\"\\\\n  },\\\\n  {\\\\n    \\\\\\"catalog_name\\\\\\": \\\\\\"其它问题\\\\\\",\\\\n    \\\\\\"question\\\\\\": \\\\\\"重复表述：第四点“拆除施工施工要单位制定……”中“施工”重复。\\\\\\",\\\\n    \\\\\\"question_tag\\\\\\": \\\\\\"重复表述问题\\\\\\",\\\\n    \\\\\\"question_exist\\\\\\": \\\\\\"true\\\\\\",\\\\n    \\\\\\"feedback\\\\\\": \\\\\\"修正为“拆除施工需由施工单位制定详细的施工方案”。\\\\\\",\\\\n    \\\\\\"feedback_exist\\\\\\": \\\\\\"true\\\\\\",\\\\n    \\\\\\"feedback_tag\\\\\\": \\\\\\"修正重复\\\\\\",\\\\n    \\\\\\"filename\\\\\\": \\\\\\"无支撑材料。\\\\\\",\\\\n    \\\\\\"content\\\\\\": \\\\\\"无支撑材料。\\\\\\",\\\\n    \\\\\\"ai_error\\\\\\": \\\\\\"\\\\\\"\\\\n  },\\\\n  {\\\\n    \\\\\\"catalog_name\\\\\\": \\\\\\"其它问题\\\\\\",\\\\n    \\\\\\"question\\\\\\": \\\\\\"标点符号不规范：部分括号为全角（如“（91#-92#）”），部分为半角（如“(二)”），建议统一为全角。\\\\\\",\\\\n    \\\\\\"question_tag\\\\\\": \\\\\\"格式问题\\\\\\",\\\\n    \\\\\\"question_exist\\\\\\": \\\\\\"true\\\\\\",\\\\n    \\\\\\"feedback\\\\\\": \\\\\\"统一使用全角符号，如“（一）”“（二）”。\\\\\\",\\\\n    \\\\\\"feedback_exist\\\\\\": \\\\\\"true\\\\\\",\\\\n    \\\\\\"feedback_tag\\\\\\": \\\\\\"统一符号格式\\\\\\",\\\\n    \\\\\\"filename\\\\\\": \\\\\\"无支撑材料。\\\\\\",\\\\n    \\\\\\"content\\\\\\": \\\\\\"无支撑材料。\\\\\\",\\\\n    \\\\\\"ai_error\\\\\\": \\\\\\"\\\\\\"\\\\n  }\\\\n]\\\\n```\\"]","annotations":null},"form":null,"image":null}],"useage":null,"metadata":{}},"thoughts":null,"error":null},"errorCode":null,"errorMsg":null,"extraData":null,"traceId":null,"env":null,"other":null,"firstErrorMessage":null,"failure":false}'

        str2 = '{"errorMessages":[],"success":true,"data":{"message":{"id":"8dc73ec7-05f4-4f2d-9450-b1bc8eb9118e","gmtCreate":"2025-07-15T02:05:14.963+00:00","sessionId":"f9b2208f-846b-43a4-a428-4bb3673d2152","requestId":"37cc42d4-7dcb-4b74-9951-587c22e5cee4","role":"assistant","content":[{"index":null,"type":"text","text":{"value":"[\\"\\\\n\\\\n```json\\\\n[\\\\n  {\\\\n    \\\\\\"catalog_name\\\\\\": \\\\\\"施工作业特点\\\\\\",\\\\n    \\\\\\"question\\\\\\": \\\\\\"原文中“拆除施工施工要单位制定详细的施工方案”存在重复用词错误\\\\\\",\\\\n    \\\\\\"question_tag\\\\\\": \\\\\\"错别字问题\\\\\\",\\\\n    \\\\\\"question_exist\\\\\\": \\\\\\"true\\\\\\",\\\\n    \\\\\\"feedback\\\\\\": \\\\\\"将“施工要单位”改为“需由施工单位”，建议修改为：\\\\\\\\\\\\\\"拆除施工需由施工单位制定详细的施工方案\\\\\\\\\\\\\\"\\\\\\",\\\\n    \\\\\\"feedback_exist\\\\\\": \\\\\\"true\\\\\\",\\\\n    \\\\\\"feedback_tag\\\\\\": \\\\\\"修改错别字\\\\\\",\\\\n    \\\\\\"filename\\\\\\": \\\\\\"无支撑材料。\\\\\\",\\\\n    \\\\\\"content\\\\\\": \\\\\\"无支撑材料。\\\\\\",\\\\n    \\\\\\"ai_error\\\\\\": \\\\\\"\\\\\\"\\\\n  },\\\\n  {\\\\n    \\\\\\"catalog_name\\\\\\": \\\\\\"施工作业特点\\\\\\",\\\\n    \\\\\\"question\\\\\\": \\\\\\"二级目录\\\\\\\\\\\\\\"(二)施工作业特点\\\\\\\\\\\\\\"中第4点存在段落缩进格式不统一问题\\\\\\",\\\\n    \\\\\\"question_tag\\\\\\": \\\\\\"结构问题\\\\\\",\\\\n    \\\\\\"question_exist\\\\\\": \\\\\\"true\\\\\\",\\\\n    \\\\\\"feedback\\\\\\": \\\\\\"建议采用与其它条目一致的缩进层级\\\\\\",\\\\n    \\\\\\"feedback_exist\\\\\\": \\\\\\"true\\\\\\",\\\\n    \\\\\\"feedback_tag\\\\\\": \\\\\\"调整格式\\\\\\",\\\\n    \\\\\\"filename\\\\\\": \\\\\\"无支撑材料。\\\\\\",\\\\n    \\\\\\"content\\\\\\": \\\\\\"无支撑材料。\\\\\\",\\\\n    \\\\\\"ai_error\\\\\\": \\\\\\"\\\\\\"\\\\n  },\\\\n  {\\\\n    \\\\\\"catalog_name\\\\\\": \\\\\\"工程概况\\\\\\",\\\\n    \\\\\\"question\\\\\\": \\\\\\"未明确工程地理位置信息。缺失地市/区县、乡镇街道及重点参照物等要素\\\\\\",\\\\n    \\\\\\"question_tag\\\\\\": \\\\\\"内容不完整\\\\\\",\\\\n    \\\\\\"question_exist\\\\\\": \\\\\\"true\\\\\\",\\\\n    \\\\\\"feedback\\\\\\": \\\\\\"补充地市/区县（如昆明市官渡区）、乡镇街道（如六甲街道）及重点参照物（如临近滇池国际会展中心）\\\\\\",\\\\n    \\\\\\"feedback_exist\\\\\\": \\\\\\"true\\\\\\",\\\\n    \\\\\\"feedback_tag\\\\\\": \\\\\\"补充内容\\\\\\",\\\\n    \\\\\\"filename\\\\\\": \\\\\\"无支撑材料。\\\\\\",\\\\n    \\\\\\"content\\\\\\": \\\\\\"无支撑材料。\\\\\\",\\\\n    \\\\\\"ai_error\\\\\\": \\\\\\"\\\\\\"\\\\n  },\\\\n  {\\\\n    \\\\\\"catalog_name\\\\\\": \\\\\\"工程概况\\\\\\",\\\\n    \\\\\\"question\\\\\\": \\\\\\"未说明工程规模量化指标\\\\\\",\\\\n    \\\\\\"question_tag\\\\\\": \\\\\\"内容不完整\\\\\\",\\\\n    \\\\\\"question_exist\\\\\\": \\\\\\"true\\\\\\",\\\\n    \\\\\\"feedback\\\\\\": \\\\\\"补充拆除线路长度（如0.8km）、涉及杆塔数量（如2基）等具体参数\\\\\\",\\\\n    \\\\\\"feedback_exist\\\\\\": \\\\\\"true\\\\\\",\\\\n    \\\\\\"feedback_tag\\\\\\": \\\\\\"补充内容\\\\\\",\\\\n    \\\\\\"filename\\\\\\": \\\\\\"无支撑材料。\\\\\\",\\\\n    \\\\\\"content\\\\\\": \\\\\\"无支撑材料。\\\\\\",\\\\n    \\\\\\"ai_error\\\\\\": \\\\\\"\\\\\\"\\\\n  },\\\\n  {\\\\n    \\\\\\"catalog_name\\\\\\": \\\\\\"施工作业特点\\\\\\",\\\\n    \\\\\\"question\\\\\\": \\\\\\"未描述工程周边环境特征\\\\\\",\\\\n    \\\\\\"question_tag\\\\\\": \\\\\\"内容不完整\\\\\\",\\\\n    \\\\\\"question_exist\\\\\\": \\\\\\"true\\\\\\",\\\\n    \\\\\\"feedback\\\\\\": \\\\\\"补充说明作业区域地形（如跨越农田）、邻近设施（如平行架设的35kV线路）、交通条件（如施工便道情况）等环境要素\\\\\\",\\\\n    \\\\\\"feedback_exist\\\\\\": \\\\\\"true\\\\\\",\\\\n    \\\\\\"feedback_tag\\\\\\": \\\\\\"补充内容\\\\\\",\\\\n    \\\\\\"filename\\\\\\": \\\\\\"无支撑材料。\\\\\\",\\\\n    \\\\\\"content\\\\\\": \\\\\\"无支撑材料。\\\\\\",\\\\n    \\\\\\"ai_error\\\\\\": \\\\\\"\\\\\\"\\\\n  },\\\\n  {\\\\n    \\\\\\"catalog_name\\\\\\": \\\\\\"施工作业特点\\\\\\",\\\\n    \\\\\\"question\\\\\\": \\\\\\"特殊作业特点描述不完整\\\\\\",\\\\n    \\\\\\"question_tag\\\\\\": \\\\\\"内容不完整\\\\\\",\\\\n    \\\\\\"question_exist\\\\\\": \\\\\\"true\\\\\\",\\\\n    \\\\\\"feedback\\\\\\": \\\\\\"增加交叉跨越情况（如跨越南绕城高速）、同塔双回线路非同步停运风险等特有风险点说明\\\\\\",\\\\n    \\\\\\"feedback_exist\\\\\\": \\\\\\"true\\\\\\",\\\\n    \\\\\\"feedback_tag\\\\\\": \\\\\\"补充内容\\\\\\",\\\\n    \\\\\\"filename\\\\\\": \\\\\\"无支撑材料。\\\\\\",\\\\n    \\\\\\"content\\\\\\": \\\\\\"无支撑材料。\\\\\\",\\\\n    \\\\\\"ai_error\\\\\\": \\\\\\"\\\\\\"\\\\n  },\\\\n  {\\\\n    \\\\\\"catalog_name\\\\\\": \\\\\\"其他问题\\\\\\",\\\\n    \\\\\\"question\\\\\\": \\\\\\"技术参数标注不规范。原文\\\\\\\\\\\\\\"110kV垦明Ⅱ回(91#-92#）\\\\\\\\\\\\\\"括号应使用全角符号\\\\\\",\\\\n    \\\\\\"question_tag\\\\\\": \\\\\\"格式问题\\\\\\",\\\\n    \\\\\\"question_exist\\\\\\": \\\\\\"true\\\\\\",\\\\n    \\\\\\"feedback\\\\\\": \\\\\\"统一为\\\\\\\\\\\\\\"（91#-92#）\\\\\\\\\\\\\\"\\\\\\",\\\\n    \\\\\\"feedback_exist\\\\\\": \\\\\\"true\\\\\\",\\\\n    \\\\\\"feedback_tag\\\\\\": \\\\\\"规范标注\\\\\\",\\\\n    \\\\\\"filename\\\\\\": \\\\\\"无支撑材料。\\\\\\",\\\\n    \\\\\\"content\\\\\\": \\\\\\"无支撑材料。\\\\\\",\\\\n    \\\\\\"ai_error\\\\\\": \\\\\\"\\\\\\"\\\\n  },\\\\n  {\\\\n    \\\\\\"catalog_name\\\\\\": \\\\\\"施工作业特点\\\\\\",\\\\n    \\\\\\"question\\\\\\": \\\\\\"安全控制要求不具体。第3点\\\\\\\\\\\\\\"高空作业安全规范\\\\\\\\\\\\\\"应明确引用标准及具体装备要求\\\\\\",\\\\n    \\\\\\"question_tag\\\\\\": \\\\\\"要求不具体\\\\\\",\\\\n    \\\\\\"question_exist\\\\\\": \\\\\\"true\\\\\\",\\\\n    \\\\\\"feedback\\\\\\": \\\\\\"明确引用标准（如GB 26859-2011），并规定坠落悬挂安全带、双控速差自锁器等具体装备要求\\\\\\",\\\\n    \\\\\\"feedback_exist\\\\\\": \\\\\\"true\\\\\\",\\\\n    \\\\\\"feedback_tag\\\\\\": \\\\\\"明确要求\\\\\\",\\\\n    \\\\\\"filename\\\\\\": \\\\\\"无支撑材料。\\\\\\",\\\\n    \\\\\\"content\\\\\\": \\\\\\"无支撑材料。\\\\\\",\\\\n    \\\\\\"ai_error\\\\\\": \\\\\\"\\\\\\"\\\\n  }\\\\n]\\\\n```\\"]","annotations":null},"form":null,"image":null}],"useage":null,"metadata":{}},"thoughts":null,"error":null},"errorCode":null,"errorMsg":null,"extraData":null,"traceId":null,"env":null,"other":null,"firstErrorMessage":null,"failure":false}' 

        str3 = '{"errorMessages":[],"success":true,"data":{"message":{"id":"e0225d7e-726a-4638-9303-03f00a96b751","gmtCreate":"2025-07-15T02:08:16.714+00:00","sessionId":"f9b2208f-846b-43a4-a428-4bb3673d2152","requestId":"27b812ab-f855-4216-874e-e758fff510b5","role":"assistant","content":[{"index":null,"type":"text","text":{"value":"[\\"\\\\n\\\\n```json\\\\n[\\\\n  {\\\\n    \\\\\\"catalog_name\\\\\\": \\\\\\"工作地点需停电的范围\\\\\\",\\\\n    \\\\\\"question\\\\\\": \\\\\\"线路名称中的编号未按“数字+‘#’”结构表述。例如“垦明Ⅱ回”“垦泽Ⅱ回”“小泽线”中的“Ⅱ”为罗马数字，未使用阿拉伯数字加“#”的规范格式。\\\\\\",\\\\n    \\\\\\"question_tag\\\\\\": \\\\\\"设备名称编号格式错误\\\\\\",\\\\n    \\\\\\"question_exist\\\\\\": \\\\\\"true\\\\\\",\\\\n    \\\\\\"feedback\\\\\\": \\\\\\"修改为“垦明2#回”“垦泽2#回”“小泽线”等，确保编号符合“电压等级(kV)+设备名称+编号(数字+‘#’)”的结构要求。\\\\\\",\\\\n    \\\\\\"feedback_exist\\\\\\": \\\\\\"true\\\\\\",\\\\n    \\\\\\"feedback_tag\\\\\\": \\\\\\"格式规范调整\\\\\\",\\\\n    \\\\\\"filename\\\\\\": \\\\\\"无支撑材料。\\\\\\",\\\\n    \\\\\\"content\\\\\\": \\\\\\"无支撑材料。\\\\\\",\\\\n    \\\\\\"ai_error\\\\\\": \\\\\\"\\\\\\"\\\\n  },\\\\n  {\\\\n    \\\\\\"catalog_name\\\\\\": \\\\\\"保留或邻近的带电线路、设备\\\\\\",\\\\n    \\\\\\"question\\\\\\": \\\\\\"填写“无”不符合审查要求，需明确说明保留带电的线路区段、同塔架设或邻近50米范围内的同走廊线路名称、区段、色标及标识牌。\\\\\\",\\\\n    \\\\\\"question_tag\\\\\\": \\\\\\"带电线路信息缺失\\\\\\",\\\\n    \\\\\\"question_exist\\\\\\": \\\\\\"true\\\\\\",\\\\n    \\\\\\"feedback\\\\\\": \\\\\\"补充具体带电线路信息，例如“保留带电线路：110kV垦明Ⅰ回N1-N15塔段（色标红色，标识牌编号XX）”，若无带电线路需注明“经核实，工作范围内无保留或邻近带电线路”。\\\\\\",\\\\n    \\\\\\"feedback_exist\\\\\\": \\\\\\"true\\\\\\",\\\\n    \\\\\\"feedback_tag\\\\\\": \\\\\\"信息补充要求\\\\\\",\\\\n    \\\\\\"filename\\\\\\": \\\\\\"无支撑材料。\\\\\\",\\\\n    \\\\\\"content\\\\\\": \\\\\\"无支撑材料。\\\\\\",\\\\n    \\\\\\"ai_error\\\\\\": \\\\\\"\\\\\\"\\\\n  },\\\\n  {\\\\n    \\\\\\"catalog_name\\\\\\": \\\\\\"其它问题分析\\\\\\",\\\\n    \\\\\\"question\\\\\\": \\\\\\"若存在分阶段停电需求（如不同线路需分时段停电），当前内容未按阶段逐项填写。\\\\\\",\\\\n    \\\\\\"question_tag\\\\\\": \\\\\\"未明确分阶段停电安排\\\\\\",\\\\n    \\\\\\"question_exist\\\\\\": \\\\\\"true\\\\\\",\\\\n    \\\\\\"feedback\\\\\\": \\\\\\"若实际存在分阶段停电，需补充说明各阶段停电范围及时间，例如“第一阶段：110kV垦明Ⅱ回全线（停电时间：X月X日8:00-18:00）”。\\\\\\",\\\\n    \\\\\\"feedback_exist\\\\\\": \\\\\\"true\\\\\\",\\\\n    \\\\\\"feedback_tag\\\\\\": \\\\\\"分阶段内容补充\\\\\\",\\\\n    \\\\\\"filename\\\\\\": \\\\\\"无支撑材料。\\\\\\",\\\\n    \\\\\\"content\\\\\\": \\\\\\"无支撑材料。\\\\\\",\\\\n    \\\\\\"ai_error\\\\\\": \\\\\\"\\\\\\"\\\\n  }\\\\n]\\\\n```\\"]","annotations":null},"form":null,"image":null}],"useage":null,"metadata":{}},"thoughts":null,"error":null},"errorCode":null,"errorMsg":null,"extraData":null,"traceId":null,"env":null,"other":null,"firstErrorMessage":null,"failure":false}'

        return AgentResponseModel.model_validate_json(random.choice((str1, str2, str3)))

    elif appkey == app_key_section_overview:
        # resp_section = random.choice(list(SectionTitleTypeMap.values()))
        # resp_text = "\n".join(mock_content_feedbacks[resp_section])

        str1 = '{"errorMessages":[],"success":true,"data":{"message":{"id":"9a6a503c-2f7b-4033-83ac-eee3f2858097","gmtCreate":"2025-07-14T08:38:15.838+00:00","sessionId":"07b84a6a-2fb7-4b0c-867d-dd7e1d6b738a","requestId":"e879aea1-7978-499b-bc6d-0fb648978c5f","role":"assistant","content":[{"index":null,"type":"text","text":{"value":"[\\"\\\\n\\\\n##错别字分析：  \\\\n1. 无错别字。  \\\\n\\\\n##结构分析：  \\\\n1. 无结构问题。  \\\\n\\\\n##二级目录“工程概况”内容审查结果分析：  \\\\n1. **缺失地理位置信息**：内容未明确工程所在的地市/区、县、乡镇/街道及周边重点参照物（如道路、建筑等）。  \\\\n   **修改建议**：补充工程地理位置，例如“本工程位于XX市XX区XX街道，邻近XX变电站/XX道路，涉及拆除同塔双回线路导、地线共XX公里”。  \\\\n2. **工程规模描述不完整**：仅提及拆除线路段，未说明具体规模（如线路长度、杆塔数量等）。  \\\\n   **修改建议**：补充工程规模，例如“拆除线路总长XX米，涉及杆塔XX基”。  \\\\n\\\\n##二级目录“施工作业特点”内容审查结果分析：  \\\\n1. **周围环境描述缺失**：未提及工程周边环境（如邻近居民区、交通要道、地形条件等）。  \\\\n   **修改建议**：补充环境信息，例如“作业区域临近农田/居民区，需注意机械操作对周边的影响”或“现场地形为丘陵，需加强设备固定措施”。  \\\\n2. **作业特点未突出特殊性**：现有内容为通用性描述，未结合本工程具体特点（如双回线路同步拆除风险）。  \\\\n   **修改建议**：增加针对性说明，例如“同塔双回线路拆除需同步协调停电，避免误碰带电线路”或“需采用分段牵引法防止导线坠落”。  \\\\n\\\\n##其它问题分析：  \\\\n1. **重复表述**：第四点“拆除施工施工要单位制定……”中“施工”重复。  \\\\n   **修改建议**：修正为“拆除施工需由施工单位制定详细的施工方案”。  \\\\n2. **标点符号不规范**：部分括号为全角（如“（91#-92#）”），部分为半角（如“(二)”），建议统一为全角。  \\\\n   **修改建议**：统一使用全角符号，如“（一）”“（二）”。\\"]","annotations":null},"form":null,"image":null}],"useage":null,"metadata":{}},"thoughts":null,"error":null},"errorCode":null,"errorMsg":null,"extraData":null,"traceId":null,"env":null,"other":null,"firstErrorMessage":null,"failure":false}'

        str2 = '{"errorMessages":[],"success":true,"data":{"message":{"id":"c78f697f-b60d-4c5d-b497-7531138ff26b","gmtCreate":"2025-07-15T02:02:16.016+00:00","sessionId":"07b84a6a-2fb7-4b0c-867d-dd7e1d6b738a","requestId":"d1629129-8a3c-44c1-ac1c-d21aa8d4e47a","role":"assistant","content":[{"index":null,"type":"text","text":{"value":"[\\"\\\\n\\\\n    ##错别字分析：  \\\\n      1.原文中“拆除施工施工要单位制定详细的施工方案”存在重复用词错误。\\\\\\"施工要单位\\\\\\"应为\\\\\\"需由施工单位\\\\\\"，建议修改为：\\\\\\"拆除施工需由施工单位制定详细的施工方案\\\\\\"。  \\\\n\\\\n    ##结构分析：  \\\\n      1.二级目录\\\\\\"(二)施工作业特点\\\\\\"中第4点\\\\\\"拆除施工施工要单位制定...\\\\\\"存在段落缩进格式不统一问题，建议采用与其它条目一致的缩进层级。  \\\\n\\\\n    ##二级目录\\\\\\"工程概况\\\\\\"内容审查结果分析：  \\\\n      1.未明确工程地理位置信息。缺失地市/区县（如昆明市官渡区）、乡镇街道（如六甲街道）及重点参照物（如临近滇池国际会展中心）等要素。  \\\\n      2.未说明工程规模量化指标。建议补充拆除线路长度（如0.8km）、涉及杆塔数量（如2基）等具体参数。  \\\\n\\\\n    ##二级目录\\\\\\"施工作业特点\\\\\\"内容审查结果分析：  \\\\n      1.未描述工程周边环境特征。应补充说明作业区域地形（如跨越农田）、邻近设施（如平行架设的35kV线路）、交通条件（如施工便道情况）等环境要素。  \\\\n      2.特殊作业特点描述不完整。建议增加交叉跨越情况（如跨越南绕城高速）、同塔双回线路非同步停运风险等特有风险点说明。  \\\\n\\\\n    ##其它问题分析：  \\\\n      1.技术参数标注不规范。原文\\\\\\"110kV垦明Ⅱ回(91#-92#）\\\\\\"括号应使用全角符号，建议统一为\\\\\\"（91#-92#）\\\\\\"。  \\\\n      2.安全控制要求不具体。第3点\\\\\\"高空作业安全规范\\\\\\"应明确引用标准（如GB 26859-2011），并规定坠落悬挂安全带、双控速差自锁器等具体装备要求。\\"]","annotations":null},"form":null,"image":null}],"useage":null,"metadata":{}},"thoughts":null,"error":null},"errorCode":null,"errorMsg":null,"extraData":null,"traceId":null,"env":null,"other":null,"firstErrorMessage":null,"failure":false}'

        str3 = '{"errorMessages":[],"success":true,"data":{"message":{"id":"fc187f7b-0d60-4efd-8636-1850d14ce0ee","gmtCreate":"2025-07-15T02:07:00.935+00:00","sessionId":"07b84a6a-2fb7-4b0c-867d-dd7e1d6b738a","requestId":"24641f54-a360-49b9-99ea-8048ad6121d8","role":"assistant","content":[{"index":null,"type":"text","text":{"value":"[\\"\\\\n\\\\n##错别字分析：  \\\\n1. 无错别字。  \\\\n\\\\n##结构分析：  \\\\n1. 无结构问题。  \\\\n\\\\n##二级目录“工作地点需停电的范围”内容审查结果分析：  \\\\n1. **设备名称编号格式错误**：  \\\\n   - 问题：线路名称中的编号未按“数字+‘#’”结构表述。例如“垦明Ⅱ回”“垦泽Ⅱ回”“小泽线”中的“Ⅱ”为罗马数字，未使用阿拉伯数字加“#”的规范格式。  \\\\n   - 建议：修改为“垦明2#回”“垦泽2#回”“小泽线”等，确保编号符合“电压等级(kV)+设备名称+编号(数字+‘#’)”的结构要求。  \\\\n\\\\n##二级目录“保留或邻近的带电线路、设备”内容审查结果分析：  \\\\n1. **带电线路信息缺失**：  \\\\n   - 问题：填写“无”不符合审查要求，需明确说明保留带电的线路区段、同塔架设或邻近50米范围内的同走廊线路名称、区段、色标及标识牌。  \\\\n   - 建议：补充具体带电线路信息，例如“保留带电线路：110kV垦明Ⅰ回N1-N15塔段（色标红色，标识牌编号XX）”，若无带电线路需注明“经核实，工作范围内无保留或邻近带电线路”。  \\\\n\\\\n##其它问题分析：  \\\\n1. **未明确分阶段停电安排**：  \\\\n   - 问题：若存在分阶段停电需求（如不同线路需分时段停电），当前内容未按阶段逐项填写。  \\\\n   - 建议：若实际存在分阶段停电，需补充说明各阶段停电范围及时间，例如“第一阶段：110kV垦明Ⅱ回全线（停电时间：X月X日8:00-18:00）”。\\"]","annotations":null},"form":null,"image":null}],"useage":null,"metadata":{}},"thoughts":null,"error":null},"errorCode":null,"errorMsg":null,"extraData":null,"traceId":null,"env":null,"other":null,"firstErrorMessage":null,"failure":false}'

        str4 = '{"errorMessages":[],"success":true,"data":{"message":{"id":"814ff31a-d75b-4bcd-b927-5710a831dd76","gmtCreate":"2025-07-15T02:08:42.036+00:00","sessionId":"07b84a6a-2fb7-4b0c-867d-dd7e1d6b738a","requestId":"4a668313-3dbd-4215-a443-e5881ab7e5ac","role":"assistant","content":[{"index":null,"type":"text","text":{"value":"{\'审查一级目录\\"作业主要内容\\"所需内容结构不够完整，请补充后再试\'}","annotations":null},"form":null,"image":null}],"useage":null,"metadata":{}},"thoughts":null,"error":null},"errorCode":null,"errorMsg":null,"extraData":null,"traceId":null,"env":null,"other":null,"firstErrorMessage":null,"failure":false}'

        str5 = '{"errorMessages":[],"success":false,"data":null,"errorCode":"PROCESS_CONCURRENCY_LOCK","errorMsg":"当前会话正在处理上个请求,请稍后","extraData":null,"traceId":null,"env":null,"other":null,"firstErrorMessage":null,"failure":false}'

        return AgentResponseModel.model_validate_json(random.choice((str1, str2, str3, str4, str5)))

    elif appkey == app_key_document_overview:
        resp_text = "\n".join(
            random.choices(mock_document_feedbacks, k=random.randint(1, 5))
        )

    else:
        # resp_text = f"智能助手回答for {payload.message.text}"

        str1 = '{"errorMessages":[],"success":true,"data":{"message":{"id":"30f0a250-01ed-42ae-b578-3f0fb7f11fd2","gmtCreate":"2025-07-10T08:07:24.738+00:00","sessionId":"bb029a1a-e360-4fd4-8632-38d64342971f","requestId":"45747fc6-8e23-4118-a2ec-7521bf435c83","role":"assistant","content":[{"index":null,"type":"text","text":{"value":"[\\"\\\\n\\\\n未找到具体支撑材料，暂不做回答。\\"]","annotations":null},"form":null,"image":null}],"useage":null,"metadata":{}},"thoughts":null,"error":null},"errorCode":null,"errorMsg":null,"extraData":null,"traceId":null,"env":null,"other":null,"firstErrorMessage":null,"failure":false}'
        str2 = '{"errorMessages":[],"success":true,"data":{"message":{"id":"b7748b1d-da5a-44a3-8b76-ca0d8296fbe1","gmtCreate":"2025-07-10T08:08:46.630+00:00","sessionId":"bb029a1a-e360-4fd4-8632-38d64342971f","requestId":"e2c8c766-2cc8-404a-b411-7b0dd8dd918f","role":"assistant","content":[{"index":null,"type":"text","text":{"value":"[\\"\\\\n\\\\n1. 回答：三措文件的规范包括明确的审批流程、管理部门职责、危险点分析、人员资质要求及考核机制。  \\\\n   引用文件名：国网海西供电公司施工“三措”计划管理实施细则（试行）  \\\\n   引用内容：  \\\\n   - 第一条明确施工“三措”计划需规范组织、安全、技术措施的审批流程，遵循“谁管理，谁审批”原则。  \\\\n   - 第三条至第八条划分各部门职责（如建设部负责电网基建项目，运维检修部负责技改、大修项目等）。  \\\\n   - 第十六条要求所有人员需经安全教育培训并考试合格，证件有效期按《国家电网公司电力安全工作规程》执行。  \\\\n   - 第十九条至第二十二条明确工程项目管理部门、设备运维单位、分管领导及安全监督部门的审核与监督职责。  \\\\n   - 第二十三条至第二十五条规定未履行责任导致安全事件的考核依据，包括《安全事故调查规程》等文件。  \\\\n\\\\n2. 回答：三措文件封面需符合编制单位、人员及盖章规范。  \\\\n   引用文件名：输电专业三措审批要点  \\\\n   引用内容：  \\\\n   - 封面编制单位必须为中标单位（非分包单位），办理人员须为工作负责人，且需盖章并填写时间。\\"]","annotations":null},"form":null,"image":null}],"useage":null,"metadata":{}},"thoughts":null,"error":null},"errorCode":null,"errorMsg":null,"extraData":null,"traceId":null,"env":null,"other":null,"firstErrorMessage":null,"failure":false}'

        return AgentResponseModel.model_validate_json(random.choice((str1, str2)))

    rand_int = random.randint(0, 100)

    has_err = rand_int % 10 == 0

    logger.info(f"模拟是否出错: {rand_int = }, { rand_int % 10 == 0 =}")

    message = None
    error = None

    if has_err:
        err1 = '{"errorMessages":[],"success":true,"data":{"message":null,"thoughts":null,"error":{"id":null,"gmtCreate":null,"sessionId":"743cb383-53c7-40de-868c-54a86704437a","requestId":null,"role":null,"content":{"errorCode":"UN_KNOW_ERROR","errorName":"未知异常","errorMsg":"{\\"text\\":\\"Cannot invoke \\\\\\"com.alibaba.agent.client.dto.SessionDTO.getUniqueCode()\\\\\\" because \\\\\\"sessionChild\\\\\\" is null\\"}","cause":null}}},"errorCode":null,"errorMsg":null,"extraData":null,"traceId":null,"env":null,"other":null,"firstErrorMessage":null,"failure":false}'
        err2 = '{"errorMessages": [], "success": true, "data": {"message": null, "thoughts": null, "error": {"id": null, "gmtCreate": null, "sessionId": "ae04de91-0813-46fd-804a-218b5867a60b", "requestId": null, "role": null, "content": {"errorCode": "AGENT_TASK_FAILED", "errorName": "Agent 任务失败", "errorMsg": "脚本节点执行失败,节点名称:[提取目录10全部内容-脚本任务], 错误信息: can only concatenate str (not \\"NoneType\\") to strTraceback (most recent call last):\\n  File \\"/home/admin/honeycomb/run/appsRoot/ibp-agent-platform_1.0.0_152/BOOT-INF/classes/ibp-script-engine/sandbox.py\\", line 147, in exec_sandbox\\n    r, g, l = secure_execute(user_codes, myglobals=global_values, mylocals=local_values,\\n  File \\"/home/admin/honeycomb/run/appsRoot/ibp-agent-platform_1.0.0_152/BOOT-INF/classes/ibp-script-engine/secure_script_executor.py\\", line 126, in secure_execute\\n    result = exec(code_obj, globals_dict)\\n  File \\"execute_output(params)\\", line 13, in <module>\\n  File \\"execute_output(params)\\", line 8, in execute_output\\nTypeError: can only concatenate str (not \\"NoneType\\") to str\\n", "cause": null}}}, "errorCode": null, "errorMsg": null, "extraData": null, "traceId": null, "env": null, "other": null, "firstErrorMessage": null, "failure": false}'

        return AgentResponseModel.model_validate_json(random.choice((err1, err2)))
        # return AgentResponseModel.model_validate_json(err1)
    else:
        message_content: list[AgentResponseDataMessageContentModel] = [
            AgentResponseDataMessageContentModel(
                type="text",
                text=AgentResponseDataMessageContentTextModel(
                    value=resp_text,  # "你好！有什么我能帮助你的吗？"
                ),
            ),
            AgentResponseDataMessageContentModel(
                type="image", image=AgentResponseDataMessageContentImageModel(url="")
            ),
        ]
        message = AgentResponseDataMessageModel(
            role="assistant", content=message_content, metadata=None
        )

    thoughts_content = AgentResponseDataThoughtsContentModel(type="text", data="")
    thoughts = AgentResponseDataThoughtsModel(
        role="assistant", content=thoughts_content
    )

    data = AgentResponseDataModel(message=message, thoughts=thoughts, error=error)
    response = AgentResponseModel(success=True, data=data)

    logger.info(f"运行智能体: {appkey =}, {payload = }, {response =}")

    return response


@router.post("/clearSession")
@router.post("/deleteSession")
def clearSession(
    auth: AppKeyDep, payload: Annotated[ClearSessionPayload, Body()]
) -> ClearSessionResponseModel:
    # if auth not in registed_app_keys:
    #     raise HTTPException(400, "该app key 不存在")

    session_id = payload.sessionId

    logger.info(f"Auth: {auth = }, clear Session => {session_id = }")

    if session_id in registed_uuid:
        registed_uuid.remove(session_id)

    return ClearSessionResponseModel(success=True)


app.include_router(router)
