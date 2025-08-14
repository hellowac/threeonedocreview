from typing import Any, NamedTuple


class HtmlParagraph(NamedTuple):
    """ 解析出的段落，数据结构 """

    content: str
    """ span标签合集 """

    tag_name: str
    """ 段落级标签名称, h1...h6 或 p """

    style_id: str = ""
    """ 段落引用的样式ID，可能为空 """

    number_text: str | None = None
    """ 如果为列表时，项目符号 """

    anchor_id: str | None = None
    """ 锚点ID """

    styles: dict[str, Any] = {}
    """ 段落的样式列表 """

    display_inline: bool = False
    """ css属性显示为单行属性 """

    last_para: bool = False
    """ vue-img、<img>标签提级后，是否为该段落的最后一个段落 """

class HtmlRun(NamedTuple):
    """ 解析出的文字run，数据结构，标签名默认span """

    content: str
    """ span文字内容，不包含标签 """

    only_space: bool
    """ 是否仅为单个空格 """

    style: str
    """ 样式列表 """
