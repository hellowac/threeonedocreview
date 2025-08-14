import random
import string
from typing import Any

from .struct import HtmlParagraph

__random_characters = string.ascii_letters + "_"

# 与段落同级的标签，需要提级处理的标签
# 这里由于前端的实现，<vue-img> 和 <img> 都需要与 <p> 标签同级才能被识别，正常显示图片，
# 所以在文字段落中内联的图片，将会在单独的一行显示，导致版式与word或wps中不一致。
# 待后期前端处理后再处理. 目前先将 <vue-img> 和 <img> 标签 提到与 <p> 标签 同级。
_p_level_tags = ("<vue-img", "<img")


def gen_random_characters(n: int) -> str:
    """生成指定长度的随机ascii字符串

    n: 字符长度
    """

    return "".join(random.choice(__random_characters) for _ in range(n))


def is_have_vue_img_tag(arr: list[str]) -> bool:
    """判断1个数组里面是否拥有vue-img标签,

    预期arr内容: ['<span...</span>', ..., '<vue-img...</vue-img>', ...]
    """

    for tag in arr:
        if tag.startswith(_p_level_tags):
            return True

    return False


def gen_paragraph_html(
    p: HtmlParagraph,
    # content: str,
    # tag_name: str,
    # number_text: Optional[str] = None,
    # anchor_id: Optional[str] = None,
    # p_tag_style: Optional[str] = None,
    # display_inline: bool = False,
) -> str:
    """将span标签 封装进指定的段落标签中

    预期效果:

    <p>
        <span ..>...</span>
        <span ..>...</span>
        <span ..>...</span>
    </p>

    预期参数

    - arr: ['<span...</span>', ..., ]
    - tag_name: p 或 h1..h6
    - anchor_id: None 或 <anchorID>
    - p_tag_style: None 或 font-size: 10pt; ....
    """

    # 段落标签样式
    if p.styles is not None:
        styles_text = "; ".join([f"{key}:{value}" for key, value in p.styles.items()])
    else:
        styles_text = ""

    if p.display_inline:
        styles_text = (
            f"{styles_text}; display: inline" if styles_text else "display: inline"
        )

    # 插入段落样式
    if styles_text and p.anchor_id:
        html_paragraph = f"<{p.tag_name} id=\"{p.anchor_id}\" style='{styles_text};'>{p.number_text or ''} {p.content}</{p.tag_name}>"

    elif styles_text:
        html_paragraph = f"<{p.tag_name} style='{styles_text};'>{p.number_text or ''} {p.content}</{p.tag_name}>"

    elif p.anchor_id:
        html_paragraph = f'<{p.tag_name} id="{p.anchor_id}" >{p.number_text or ""} {p.content}</{p.tag_name}>'

    else:
        html_paragraph = (
            f"<{p.tag_name}  >{p.number_text or ''} {p.content}</{p.tag_name}>"
        )

    if p.display_inline and p.last_para:
        html_paragraph = html_paragraph + "<br/>"

    return html_paragraph


def gen_paragraph_shtml(
    p: HtmlParagraph,
    # content: str,
    # tag_name: str,
    # number_text: Optional[str] = None,
    # anchor_id: Optional[str] = None,
    # p_tag_style: Optional[str] = None,
    # display_inline: bool = False,
) -> str:
    """将span标签 封装进指定的段落标签中

    预期效果:

    <p>
        <span ..>...</span>
        <span ..>...</span>
        <span ..>...</span>
    </p>

    预期参数

    - arr: ['<span...</span>', ..., ]
    - tag_name: p 或 h1..h6
    - anchor_id: None 或 <anchorID>
    - p_tag_style: None 或 font-size: 10pt; ....
    """

    html_paragraph = f"<{p.tag_name}>{p.number_text or ''} {p.content}</{p.tag_name}>"

    if p.display_inline and p.last_para:
        html_paragraph = html_paragraph + "<br/>"

    return html_paragraph


def gen_html_paragraph(
    arr: list[str],
    tag_name: str,
    style_id: str,
    number_text: str | None = None,
    anchor_id: str | None = None,
    p_styles: dict[str, Any] | None = None,
    display_inline: bool = False,
    last_para: bool = False,
) -> HtmlParagraph:
    """将span标签 封装进指定的段落标签中

    预期效果:

    <p>
        <span ..>...</span>
        <span ..>...</span>
        <span ..>...</span>
    </p>

    预期参数

    - arr: ['<span...</span>', ..., ]
    - tag_name: p 或 h1..h6
    - anchor_id: None 或 <anchorID>
    - p_tag_style: None 或 font-size: 10pt; ....
    """

    p_content = (
        "".join(arr) if arr else "<span>&nbsp;</span>"
    )  # 空arr则赋予一个带空格的span，表示新的1个段落，否则前端html渲染不出来这一个段落.

    return HtmlParagraph(
        p_content,
        tag_name,
        style_id,
        number_text,
        anchor_id,
        p_styles or {},
        display_inline,
        last_para,
    )


def gen_shtml_paragraph(
    arr: list[str],
    tag_name: str,
    style_id: str,
    number_text: str | None = None,
    anchor_id: str | None = None,
    p_styles: dict[str, Any] | None = None,
    display_inline: bool = False,
    last_para: bool = False,
) -> HtmlParagraph:
    """将span标签 封装进指定的段落标签中

    预期效果:

    <p>
        ...
    </p>

    预期参数

    - arr: ['<span...</span>', ..., ]
    - tag_name: p 或 h1..h6
    - anchor_id: None 或 <anchorID>
    - p_tag_style: None 或 font-size: 10pt; ....
    """

    p_content = (
        "".join(arr) if arr else " "
    )  # 空arr则赋予一个带空格的span，表示新的1个段落，否则前端html渲染不出来这一个段落.

    return HtmlParagraph(
        p_content,
        tag_name,
        style_id,
        number_text,
        anchor_id,
        p_styles or {},
        display_inline,
        last_para,
    )


def gen_txt_paragraph(
    arr: list[str],
    tag_name: str,
    style_id: str,
    number_text: str | None = None,
    anchor_id: str | None = None,
    p_styles: dict[str, Any] | None = None,
    display_inline: bool = False,
    last_para: bool = False,
) -> HtmlParagraph:
    """将span标签 封装进指定的段落标签中

    预期效果:

    p1...

    预期参数

    - arr: ['<span...</span>', ..., ]
    - tag_name: p 或 h1..h6
    - anchor_id: None 或 <anchorID>
    - p_tag_style: None 或 font-size: 10pt; ....
    """

    p_content = (
        "".join(arr) if arr else " "
    )  # 空arr则赋予一个带空格的span，表示新的1个段落，否则前端html渲染不出来这一个段落.

    return HtmlParagraph(
        p_content,
        tag_name,
        style_id,
        number_text,
        anchor_id,
        p_styles or {},
        display_inline,
        last_para,
    )


def get_wh_from_vml_sp_style(style: str) -> tuple[str, str]:
    """从基于vml的shape元素的style属性中获取宽高

    xml实例:

        <v:shape id="_x0000_i1025" o:spt="75" type="#_x0000_t75" style="height:18pt;width:13.9pt;" o:ole="t" filled="f" o:preferrelative="t" stroked="f" coordsize="21600,21600">
            ...
        </v:shape>

    预期:

    style: str, 例如: "height:18pt;width:13.9pt;"

    结果:

    (width, height) = 13.9pt, 18pt
    """

    kv_str = style.split(";")
    kv_map = dict(kv.split(":") for kv in kv_str if kv)

    width = kv_map.get("width", "0pt")
    height = kv_map.get("height", "0pt")

    return width, height


def gen_paragraph_txt(p: HtmlParagraph) -> str:
    """将span标签 封装进指定的段落标签中

    预期效果:

    paratxt1

    预期参数

    - arr: ['txt', ..., ]
    - tag_name: p 或 h1..h6
    - anchor_id: None 或 <anchorID>
    - p_tag_style: None 或 font-size: 10pt; ....
    """

    txt_paragraph = f'{p.number_text or ""}{p.content}'

    if p.display_inline and p.last_para:
        txt_paragraph += "\n"

    return txt_paragraph
