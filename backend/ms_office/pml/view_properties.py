from .parts import ViewProperitesPart


class ViewProperties:
    """视窗属性封装类"""

    def __init__(self, part: ViewProperitesPart) -> None:
        """
        视窗属性封装类

        参考: http://192.168.2.53:8001/openxml/ecma-part1/chapter-13/#13313-视图属性部件
        """

        self.part = part
        self.oxml = part.oxml
