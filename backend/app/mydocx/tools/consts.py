from enum import Enum
from typing import Any


class BaseEnumType(Enum):
    """参考:

    合法的枚举成员和属性

    https://docs.python.org/zh-cn/3.10/library/enum.html#allowed-members-and-attributes-of-enumerations
    """

    @classmethod
    def have_value(cls, value: Any):
        """判断是否拥有某个值"""

        return value in [e.value for e in cls]


class FileType(int, BaseEnumType):
    """解析到的对象对应的文件类型，要与给前端的资源库中的文件类型一致,

    参考: yunpan/store/models/FileDirModel.py 中的  Files.FileTypeChoice 定义.

    """

    IMAGE = 1
    VIDEO = 2
    AUDIO = 3
    DOC = 4
    THREE_D = 5
    OTHER = 6
    EBOOK = 7
    COURSEWARE = 8
    MOBILE = 9
    VR = 10
    TWO_D = 20
    XNFZ = 30  # 虚拟仿真
    KNOWLEDGEMAP = 11

    FEBK = 101
    ALL = 99


class HeadingType(str, BaseEnumType):
    """标题样式ID 枚举"""

    Heading1 = "Heading1"
    Heading2 = "Heading2"
    Heading3 = "Heading3"
    Heading4 = "Heading4"
    Heading5 = "Heading5"
    Heading6 = "Heading6"

    # HeadingName1 = heading 3

    HeadingName1 = "heading 1"
    HeadingName2 = "heading 2"
    HeadingName3 = "heading 3"
    HeadingName4 = "heading 4"
    HeadingName5 = "heading 5"
    HeadingName6 = "heading 6"


HeadingTypeTagMap = {
    HeadingType.Heading1: "h1",
    HeadingType.Heading2: "h2",
    HeadingType.Heading3: "h3",
    HeadingType.Heading4: "h4",
    HeadingType.Heading5: "h5",
    HeadingType.Heading6: "h6",
    HeadingType.HeadingName1: "h1",
    HeadingType.HeadingName2: "h2",
    HeadingType.HeadingName3: "h3",
    HeadingType.HeadingName4: "h4",
    HeadingType.HeadingName5: "h5",
    HeadingType.HeadingName6: "h6",
}
