from pydantic import BaseModel, Field, RootModel, computed_field

from app.core.config import settings

# --------------- session 创建/清理相关 -------------


class CreateSessionPayload(BaseModel):
    """创建session需要的参数"""

    agentCode: str
    agentVersion: str


class CreateSessionResponseDataModel(BaseModel):
    """生成的会话ID"""

    uniqueCode: str = Field(description="sesion ID")


class CreateSessionResponseModel(BaseModel):
    # {
    #     "success": True,
    #     "data": {"uniqueCode": session_id},
    #     "errorCode": None,
    #     "errorMsg": None,
    # }

    success: bool = Field(description="是否成功")
    data: CreateSessionResponseDataModel = Field(description="生成的会话ID")
    errorCode: str | None = Field(default=None, description="业务错误码")
    errorMsg: str | None = Field(default=None, description="业务错误描述")


# -------------- session清理 -----------


class ClearSessionPayload(BaseModel):
    """清理session需要的参数"""

    sessionId: str


class ClearSessionResponseModel(BaseModel):
    """清理session的回话"""

    success: bool = Field(description="是否成功")


# ------- agent 请求数据结构 ------------


class RunAgentMessageAttachmentPayload(BaseModel):
    """附件信息结构体"""

    url: str = Field(description="附件地址")
    name: str | None = Field(description="附件名称")


class RunAgentMessagePayload(BaseModel):
    """调用智能体的message结构定义"""

    text: str = Field(description="对话输入")
    metadata: dict = Field(default_factory=lambda: {}, description="扩展信息")
    attachments: list[RunAgentMessageAttachmentPayload] = Field(
        default_factory=lambda: [], description="附件信息"
    )


class RunAgentPayload(BaseModel):
    """运行智能体的参数"""

    sessionId: str = Field(description="会话ID")
    stream: bool = Field(description="是否流式")
    delta: bool = Field(
        default=True,
        description="当stream=true，控制是否不追加新文本, 例如: true 默从每次输出新内容，不包含前序输出的文本",
    )
    trace: bool = Field(
        default=False,
        description="当trace=true，控制是否返回trace记录, 例如: false 颗认不返回trace记录",
    )

    message: RunAgentMessagePayload = Field(description="请求消息体")


# ------- agent 响应数据结构 ------------


class AgentResponseDataMessageContentTextModel(BaseModel):
    value: str = Field(description="输出文本")


class AgentResponseDataMessageContentImageModel(BaseModel):
    url: str = Field(description="输出图片的地址")


class AgentResponseDataMessageContentModel(BaseModel):
    type: str = Field(description="输出内容类型, text/image, 其他类型未知")
    text: AgentResponseDataMessageContentTextModel | None = Field(
        default=None, description="type=text 场景的输出结构"
    )
    image: AgentResponseDataMessageContentImageModel | None = Field(
        default=None, description="type=image 场景的输出结构"
    )


class AgentResponseDataMessageModel(BaseModel):
    role: str = Field(description="角色")
    metadata: dict | None = Field(default=None, description="扩展字段")
    content: list[AgentResponseDataMessageContentModel] = Field(description="输出内容")


class AgentResponseDataThoughtsContentModel(BaseModel):
    data: str = Field(description="输出文本")
    type: str = Field(description="输出内容类型，目前是常量 text")


class AgentResponseDataThoughtsModel(BaseModel):
    role: str = Field(description="角色")
    content: AgentResponseDataThoughtsContentModel = Field(description="揃出内容")


class AgentResponseDataErrorContentModel(BaseModel):
    """agent 执行任务过程中的报错信息 内容

    "content": {
        "errorCode": "AGENT_TASK_FAILED",
        "errorName": "Agent 任务失败",
        "errorMsg": "脚本节点执行失败,节点名称:[提取目录10全部内容-脚本任务], 错误信息: can only concatenate str (not \"NoneType\") to strTraceback (most recent call last):\n  File \"/home/admin/honeycomb/run/appsRoot/ibp-agent-platform_1.0.0_152/BOOT-INF/classes/ibp-script-engine/sandbox.py\", line 147, in exec_sandbox\n    r, g, l = secure_execute(user_codes, myglobals=global_values, mylocals=local_values,\n  File \"/home/admin/honeycomb/run/appsRoot/ibp-agent-platform_1.0.0_152/BOOT-INF/classes/ibp-script-engine/secure_script_executor.py\", line 126, in secure_execute\n    result = exec(code_obj, globals_dict)\n  File \"execute_output(params)\", line 13, in <module>\n  File \"execute_output(params)\", line 8, in execute_output\nTypeError: can only concatenate str (not \"NoneType\") to str\n",
        "cause": null
    }
    """

    errorCode: str | None = Field(default=None, description="错误码")
    errorName: str | None = Field(default=None, description="错误名称")
    errorMsg: str | None = Field(default=None, description="错误消息")
    cause: str | None = Field(default=None, description="...")


class AgentResponseDataErrorModel(BaseModel):
    """agent 执行任务过程中的报错信息

    "error": {
        "id": null,
        "gmtCreate": null,
        "sessionId": "ae04de91-0813-46fd-804a-218b5867a60b",
        "requestId": null,
        "role": null,
        "content": {
            "errorCode": "AGENT_TASK_FAILED",
            "errorName": "Agent 任务失败",
            "errorMsg": "脚本节点执行失败,节点名称:[提取目录10全部内容-脚本任务], 错误信息: can only concatenate str (not \"NoneType\") to strTraceback (most recent call last):\n  File \"/home/admin/honeycomb/run/appsRoot/ibp-agent-platform_1.0.0_152/BOOT-INF/classes/ibp-script-engine/sandbox.py\", line 147, in exec_sandbox\n    r, g, l = secure_execute(user_codes, myglobals=global_values, mylocals=local_values,\n  File \"/home/admin/honeycomb/run/appsRoot/ibp-agent-platform_1.0.0_152/BOOT-INF/classes/ibp-script-engine/secure_script_executor.py\", line 126, in secure_execute\n    result = exec(code_obj, globals_dict)\n  File \"execute_output(params)\", line 13, in <module>\n  File \"execute_output(params)\", line 8, in execute_output\nTypeError: can only concatenate str (not \"NoneType\") to str\n",
            "cause": null
        }
    }
    """

    id: str | None = Field(default=None, description="错误ID")
    gmtCreate: str | None = Field(default=None, description="...")
    sessionId: str | None = Field(default=None, description="会话ID")
    requestId: str | None = Field(default=None, description="...")
    role: str | None = Field(default=None, description="...")
    content: AgentResponseDataErrorContentModel | None = Field(
        default=None, description="错误数据消息"
    )


class AgentResponseDataModel(BaseModel):
    message: AgentResponseDataMessageModel | None = Field(
        default=None, description="输出文本响应"
    )
    thoughts: AgentResponseDataThoughtsModel | None = Field(
        default=None, description="输出思考响应"
    )
    error: AgentResponseDataErrorModel | None = Field(
        default=None, description="执行任务过程中的报错信息"
    )


class AgentResponseModel(BaseModel):
    """agent非流式响应格式

    {
        "errorMessages": [],
        "success": true,
        "data": {
            "message": null,
            "thoughts": null,
            "error": {
                "id": null,
                "gmtCreate": null,
                "sessionId": "ae04de91-0813-46fd-804a-218b5867a60b",
                "requestId": null,
                "role": null,
                "content": {
                    "errorCode": "AGENT_TASK_FAILED",
                    "errorName": "Agent 任务失败",
                    "errorMsg": "脚本节点执行失败,节点名称:[提取目录10全部内容-脚本任务], 错误信息: can only concatenate str (not \"NoneType\") to strTraceback (most recent call last):\n  File \"/home/admin/honeycomb/run/appsRoot/ibp-agent-platform_1.0.0_152/BOOT-INF/classes/ibp-script-engine/sandbox.py\", line 147, in exec_sandbox\n    r, g, l = secure_execute(user_codes, myglobals=global_values, mylocals=local_values,\n  File \"/home/admin/honeycomb/run/appsRoot/ibp-agent-platform_1.0.0_152/BOOT-INF/classes/ibp-script-engine/secure_script_executor.py\", line 126, in secure_execute\n    result = exec(code_obj, globals_dict)\n  File \"execute_output(params)\", line 13, in <module>\n  File \"execute_output(params)\", line 8, in execute_output\nTypeError: can only concatenate str (not \"NoneType\") to str\n",
                    "cause": null
                }
            }
        },
        "errorCode": null,
        "errorMsg": null,
        "extraData": null,
        "traceId": null,
        "env": null,
        "other": null,
        "firstErrorMessage": null,
        "failure": false
    }
    """

    success: bool = Field(description="业务是否成功!")
    data: AgentResponseDataModel | None = Field(default=None, description="业务响应")
    errorCode: str | None = Field(default=None, description="业务错误码")
    errorMsg: str | None = Field(default=None, description="业务错误描述")


# -------- 系统分析 概览数据的 schema 定义 -------------


class AnalysisOverviewTotal(BaseModel):
    title: str = Field(description="总量名称, 比如: 项目总量")
    total: int = Field(description="总量值, 比如: 1923")
    prevTotal: int = Field(description="上一总量值, 比如: 1000")
    iconClass: str = Field(description="icon类, 比如: el-icon-folder-opened")
    iconColor: str = Field(description="icon颜色, 比如: #0066CC")
    isUp: bool = Field(description="是否为提升, 比如: true")
    amplitude: str = Field(description="提升/降低百分比, 比如: 5%")


class PieChartItem(BaseModel):
    name: str = Field(description="名称")
    value: float = Field(description="值")


AnalysisPieChartData = RootModel[list[PieChartItem]]


class AnalysisBarChartData(BaseModel):
    # 值和分类的合集的长度应该相等
    categoryData: list[str] = Field(description="分类合集")
    chartdata: list[float] = Field(description="值合集")


class PieCurPrevData(BaseModel):
    all: AnalysisPieChartData = Field(description="日期分类为【所有】时的pie数据")
    cur: AnalysisPieChartData = Field(description="日期分类为【日/月/年】时的pie数据")
    prev: AnalysisPieChartData = Field(description="日期分类为【日/月/年】时的pie数据")


class BarCurPrevData(BaseModel):
    all: AnalysisBarChartData = Field(description="日期分类为【所有】时的bar数据")
    cur: AnalysisBarChartData = Field(description="日期分类为【日/月/年】时的bar数据")
    prev: AnalysisBarChartData = Field(description="日期分类为【日/月/年】时的bar数据")


class QuestionSuggestionChartData(BaseModel):
    pieData: PieCurPrevData = Field(description="pie图的数据")
    barData: BarCurPrevData = Field(description="bar图的数据")


# ---------------- isc oss 登录 相关 shcema ------------------


class IscLoginPayload(BaseModel):
    """根据isc oss登录后的ticket获取用户信息"""

    ticket: str = Field(description="isc oss 登录成功后，获取到的票据(ticket)")
    service: str = Field(description="羡慕前端访问根地址")


class TicketTokenResp(BaseModel):
    """ticket转token后的返回数据结构"""

    access_token: str = Field(description="获取用户信息的凭证")
    expires_in: int = Field(description="凭证多少秒后过期")


class UserinfoResp(BaseModel):
    """根据token获取用户信息的数据结构

    返回示例
    {
        "id": "1F4957AA20594E2D8F1E920DFE0CE385",
        "username": "lbhai5217",
        "name": "李宝海",
        "orgId": "8B9669DF65ED55D1E053E31BD70A70E4"
    }
    """

    id: str = Field(description="用户ID，唯一")
    username: str = Field(description="用户登录名，唯一")
    name: str = Field(description="用户显示的中文名")
    orgId: str = Field(description="用户的组织ID")

    @computed_field  # type: ignore
    @property
    def is_superuser(self) -> bool:
        """判断用户是否为超级用户"""

        return self.username == settings.SUPERUSER_USERNAME


class IscLoginSuccessResp(BaseModel):
    code: int = Field(default=200, description="状态码")
    message: str | None = Field(default=None, description="错误消息")
    jwt: str = Field(description="校验的token")
    user: UserinfoResp = Field(description="用户信息")

# -------------- ocr 识别结果相关 schema ----------------------

class PdfOcrTextBlock(BaseModel):

    rec_text: str | None = None
    rec_score: float | None = None
    det_poly: list[tuple[float, float]]  # 4个坐标
    det_box: list[float]  # 4个元素


class PdfOcrText(BaseModel):

    text_blocks: list[PdfOcrTextBlock]
    rec_score: float


class PdfOcrResData(BaseModel):

    ocr_text: PdfOcrText


class PdfOcrResResponse(BaseModel):
    """ 示例:

    ```json
    {
        "code": 0,
        "msg": "ok",
        "data": {
            "ocr_text": {
            "text_blocks": [
                {
                "rec_text": "青海海西格尔木昆开110kV变电站10kV",
                "rec_score": 0.9959395527839661,
                "det_poly": [
                    [
                    177,
                    338
                    ],
                    [
                    1013,
                    328
                    ],
                    [
                    1013,
                    379
                    ],
                    [
                    177,
                    388
                    ]
                ],
                "det_box": [
                    177,
                    328,
                    1013,
                    388
                ]
                },
                {
                "rec_text": "Ⅲ期配出工程",
                "rec_score": 0.9996023774147034,
                "det_poly": [
                    [
                    446,
                    398
                    ],
                    [
                    741,
                    395
                    ],
                    [
                    742,
                    446
                    ],
                    [
                    447,
                    449
                    ]
                ],
                "det_box": [
                    446,
                    395,
                    742,
                    449
                ]
                },
                {
                "rec_text": "组织技术安全措施",
                "rec_score": 0.9992884993553162,
                "det_poly": [
                    [
                    415,
                    526
                    ],
                    [
                    771,
                    522
                    ],
                    [
                    772,
                    570
                    ],
                    [
                    416,
                    574
                    ]
                ],
                "det_box": [
                    415,
                    522,
                    772,
                    574
                ]
                },
                {
                "rec_text": "编制单位：格尔木海电实业有限责任公司",
                "rec_score": 0.9957185387611389,
                "det_poly": [
                    [
                    347,
                    1190
                    ],
                    [
                    925,
                    1187
                    ],
                    [
                    925,
                    1222
                    ],
                    [
                    347,
                    1224
                    ]
                ],
                "det_box": [
                    347,
                    1187,
                    925,
                    1224
                ]
                },
                {
                "rec_text": "20年",
                "rec_score": 0.6889985203742981,
                "det_poly": [
                    [
                    533,
                    1240
                    ],
                    [
                    756,
                    1240
                    ],
                    [
                    756,
                    1311
                    ],
                    [
                    533,
                    1311
                    ]
                ],
                "det_box": [
                    533,
                    1240,
                    756,
                    1311
                ]
                }
            ],
            "rec_score": 0.9359094977378846
            }
        }
    }
    ```
    """

    code: int
    msg: str
    data: PdfOcrResData