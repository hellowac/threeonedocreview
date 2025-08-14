from enum import StrEnum


class SaveType(StrEnum):
    LOCAL = "local"
    OSS = "oss"


class ProjectTypeEnum(StrEnum):
    TRNAS = "输电"
    SUBSTATION = "变电"
    DISTRIBUTION = "配电"


class FileCategory(StrEnum):
    THREESTEP = "三措文档"
    # METTING = "会议纪要"
    FEASIBIBITY = "可研材料"
    SURVEY = "勘察单"
    OTHER = "其他材料"


class ThreeoneOtherCategory(StrEnum):
    METTING = "会议纪要"
    FEASIBIBITY = "可研材料"
    SURVEY = "勘察单"
    OTHER = "其他材料"


class ReviewStatus(StrEnum):
    UNREVIEWED = "文档解析中"
    AI_REVIEW_FAILURE = "算法审核失败"
    AI_REVIEW_NOTPASS = "算法审核未通过"
    AI_REVIEW_PASSED = "算法审核通过"
    HUMAN_REVIEW_FAILD = "人工复核未通过"
    HUMAN_REVIEW_PASSED = "人工复核通过"


class SectionType(StrEnum):
    """三措文档的十条标题节点"""

    all = "文档全部内容"
    head = "文档头/封面"  # 标题封面, 以及 一、工程概况及施工作业特点 之前的内容
    one = "一、工程概况及施工作业特点"
    two = "二、施工作业计划工期、开(峻)工时间"
    three = "三、停电范围"
    four = "四、作业主要内容"
    five = "五、组织措施"
    six = "六、技术措施"
    seven = "七、安全措施"
    eight = "八、应急处置措施"
    nine = "九、施工作业工艺标准及验收"
    ten = "十、现场作业示意图"


SectionTitleTypeMap = {
    "一、工程概况及施工作业特点": SectionType.one,
    "二、施工作业计划工期、开(峻)工时间": SectionType.two,
    "三、停电范围": SectionType.three,
    "四、作业主要内容": SectionType.four,
    "五、组织措施": SectionType.five,
    "六、技术措施": SectionType.six,
    "七、安全措施": SectionType.seven,
    "八、应急处置措施": SectionType.eight,
    "九、施工作业工艺标准及验收": SectionType.nine,
    "十、现场作业示意图": SectionType.ten,
}

SectionPriorityMap: dict[SectionType, int] = {
    SectionType.all: -1,
    SectionType.head: 0,
    SectionType.one: 1,
    SectionType.two: 2,
    SectionType.three: 3,
    SectionType.four: 4,
    SectionType.five: 5,
    SectionType.six: 6,
    SectionType.seven: 7,
    SectionType.eight: 8,
    SectionType.nine: 9,
    SectionType.ten: 10,
}

# 审查section时的相关上下文section
SectionContextRelated: dict[SectionType, set[SectionType]] = {
    SectionType.one: {SectionType.one,},
    SectionType.three: {SectionType.three,},
    SectionType.four: {SectionType.two, SectionType.four},
    SectionType.five: {SectionType.five,},
    SectionType.seven: {SectionType.one, SectionType.two, SectionType.five, SectionType.six, SectionType.seven},
    SectionType.eight: {SectionType.seven, SectionType.eight},
    SectionType.nine: {SectionType.six, SectionType.nine},
}


class EnumType(StrEnum):
    """文档用到的所有枚举类型"""

    FILECATEGORY = "file_category"
    REVIEWSTATUS = "review_status"
    SECTIONTYPE = "section_type"
    WORKTYPE = "work_type"


EnumTypeMap: dict[EnumType, type[StrEnum]] = {
    EnumType.FILECATEGORY: FileCategory,
    EnumType.REVIEWSTATUS: ReviewStatus,
    EnumType.SECTIONTYPE: SectionType,
    EnumType.WORKTYPE: ProjectTypeEnum,
}


class AgentType(StrEnum):
    """ 智能体类型"""

    transmission = '输电'
    substation = '变电'
    distribute = '配电'
    assistant = '智能助手'


class ForSection(StrEnum):
    """ 智能体分类 """

    one = '第一节'
    two = '第二节'
    three = '第三节'
    four = '第四节'
    five = '第五节'
    six = '第六节'
    sevenone = '第七节(一)'
    seventwo = '第七节(二)'
    seventhree = '第七节(三)'
    sevenfour = '第七节(四)'
    eight = '第八节'
    nine = '第九节'
    ten = '第十节'

    # --- 不属于 文档审查 ------
    assistant = '智能助手'
